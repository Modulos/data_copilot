import logging
import uuid
from typing import Tuple, List

import openai
from celery import Celery, chain
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded

from data_copilot.celery_app.config import Config
from data_copilot.celery_app.crud.chats import crud_create_message
from data_copilot.celery_app.database.psql import SessionLocal, engine
from data_copilot.db_models.base import Base
from data_copilot.execution_apps import get_app

Base.metadata.create_all(bind=engine)


CONFIG = Config()

execution_app = Celery("main", broker=CONFIG.CELERY_BROKER_URL)


@execution_app.task(
    name="save_result",
    soft_time_limit=10,
    autoretry_for=(MemoryError,),
    retry_kwargs={"max_retries": 2, "countdown": 1},
)
def save_result(
    prompt_result: Tuple[str, str],
    chat_id: uuid.UUID,
    artifact_version_id: uuid.UUID | None = None,
    message_id: uuid.UUID | None = None,
):
    """Save the final result as message in the DB.

    Args:
        prompt_result (Tuple[str, str]): Tuple of message type and message content.
        chat_id (uuid.UUID): Chat id of the message.
        artifact_version_id (uuid.UUID, optional): Artifact version id of the message.
            Defaults to None.
        message_id (uuid.UUID, optional): Message id of the message. Defaults to None.

    """
    try:
        message_type, message_content = prompt_result
        db = SessionLocal()
        crud_create_message(
            db,
            chat_id,
            artifact_version_id,
            message_content,
            message_type,
        )
        db.close()
    except SoftTimeLimitExceeded:
        logging.error(
            "The task save_result exceeded the time limit --"
            f"message_id: {message_id} --"
        )
        raise TimeLimitExceeded()
    except Exception as e:
        logging.error(
            f"An error occured while saving the final result in DB: {e} --"
            f"message_id: {message_id} --"
        )
        raise e


@execution_app.task(
    name="executing_user_prompt",
    soft_time_limit=60,
    autoretry_for=(TimeLimitExceeded, openai.error.RateLimitError),
    retry_kwargs={"max_retries": 3, "countdown": 30},
)
def execute_user_prompt(
    user_prompt: str,
    chat_id: uuid.UUID,
    message_id: uuid.UUID,
    artifact_version_id: uuid.UUID,
    artifact_version_uri: str,
    previous_messages: List[dict] = None,
) -> Tuple[str, str]:
    """Execute user prompt into method to be called

    Args:
        user_prompt (str): User prompt to be translated.
        chat_id (uuid.UUID): Chat id of the message.
        message_id (uuid.UUID): Message id of the message.
        artifact_version_id (uuid.UUID): Artifact version id of the message.
        artifact_version_uri (str): Artifact version uri of the message.

    Returns:
        Tuple[str, str]: Tuple of message type and message content.
    """

    try:
        result = (
            get_app()
            .execute_message(
                user_prompt=user_prompt,
                chat_id=chat_id,
                message_id=message_id,
                artifact_version_id=artifact_version_id,
                artifact_version_uri=artifact_version_uri,
                previous_messages=previous_messages,
            )
            .to_dict()
        )
        return result["message_type"], result["text_content"]

    except SoftTimeLimitExceeded:
        logging.error(
            "The translation of the user prompt timed out --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )
        raise TimeLimitExceeded()
    except Exception as e:
        logging.error(
            f"An error occured while translating the user prompt: {e} --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )
        logging.exception(e)
        return "error", "An error occured while executing the user prompt."


@execution_app.task(name="execute_user_message")
def execute_user_message(
    user_prompt: str,
    chat_id: uuid.UUID,
    message_id: uuid.UUID,
    artifact_version_id: uuid.UUID | None = None,
    artifact_version_uri: str | None = None,
    previous_messages: List[dict] = None,
):
    chain(
        execute_user_prompt.s(
            user_prompt=user_prompt,
            chat_id=chat_id,
            message_id=message_id,
            artifact_version_id=artifact_version_id,
            artifact_version_uri=artifact_version_uri,
            previous_messages=previous_messages,
        ),
        save_result.s(
            chat_id=chat_id,
            artifact_version_id=artifact_version_id,
            message_id=message_id,
        ),
    )()
