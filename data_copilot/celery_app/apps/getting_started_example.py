import logging
import uuid
from typing import Tuple

import openai
from celery import Celery, chain
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded

from data_copilot.celery_app.config import Config
from data_copilot.celery_app.crud.chats import crud_create_message
from data_copilot.celery_app.database.psql import SessionLocal
from data_copilot.celery_app.executors import getting_started_executor

CONFIG = Config()

execution_app = Celery("main", broker=CONFIG.CELERY_BROKER_URL)


@execution_app.task(name="save_result", soft_time_limit=3)
def save_result(
    prompt_result: Tuple[str, str],
    chat_id: uuid.UUID,
    artifact_version_id: uuid.UUID | None = None,
    sas_url: str | None = None,
    artifact_config: dict | None = None,
    message_id: uuid.UUID | None = None,
):
    """Save the final result as message in the DB.

    Args:
        message_content (dict): _description_
        message_type (str): _description_
        chat_id (uuid.UUID): _description_
        artifact_version_id (uuid.UUID | None, optional): _description_.
        Defaults to None.
        sas_url (str | None, optional): _description_. Defaults to None.
        artifact_config (dict | None, optional): _description_. Defaults to None.
        message_id (uuid.UUID | None, optional): _description_. Defaults to None.
    """
    try:
        message_content, message_type = prompt_result
        db = SessionLocal()
        crud_create_message(
            db,
            chat_id,
            None,
            True,
            artifact_version_id,
            message_content,
            message_type,
        )
        logging.debug(
            f"I save the final result into DB as a message: {message_content}"
        )
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


@execution_app.task(name="execute_prompt", soft_time_limit=30)
def execute_prompt(
    query: str,
    sas_url: str | None = None,
    artifact_config: dict | None = None,
    message_id: uuid.UUID | None = None,
) -> Tuple[str, str]:
    """Execute the corresponding method and save the result

    Args:
        query (str): The sql_query
        sas_url (str): The url of the file to be analyzed.
        artifact_config (dict): The config from which the file schema is extracted.
        message_id (uuid.UUID): _description_

    Returns:
        Tuple[str, str]: The result of the execution and the type of the result.
    """
    try:
        schema = artifact_config.get("files", [dict()])[0].get("file_schema", {})
        file_type = artifact_config.get("files", [dict()])[0].get("file_type", "")

        message = getting_started_executor.run(
            sas_url, schema, file_type, query, schema.keys()
        )

        return message["text_content"], message["message_type"]
    except SoftTimeLimitExceeded:
        logging.error(
            "The execution of the prompt timed out --" f"message_id: {message_id} --"
        )
        return "The execution of the prompt timed out", "error"

    except Exception as e:
        logging.error(
            f"An error occurred while executing method: {e} -- "
            f"message_id: {message_id}"
        )
        return "An error occurred while executing method", "error"


@execution_app.task(
    name="translating_user_prompt",
    soft_time_limit=8,
    autoretry_for=(TimeLimitExceeded, openai.error.RateLimitError),
    retry_kwargs={"max_retries": 3, "countdown": 30},
)
def translate_user_prompt(
    user_prompt: str, message_id: uuid.UUID, artifact_config: dict | None = None
) -> str:
    """Translate user prompt into method to be called

    Args:
        user_prompt (str): Prompt passed from the user message to be executed.
        message_id (uuid.UUID): message id of the prompt.
        artifact_config (dict):

    Returns:
        str:
    """
    try:
        artifact_config.get("files", [dict()])[0].get("file_schema", {})

        # put here your translation logic
        query = "dummy query"

        return query

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


@execution_app.task(name="execute_user_message")
def execute_user_message(
    user_prompt: str,
    chat_id: uuid.UUID,
    message_id: uuid.UUID,
    artifact_version_id: uuid.UUID | None = None,
    sas_url: str | None = None,
    artifact_config: dict | None = None,
):
    chain(
        translate_user_prompt.s(
            user_prompt, message_id=message_id, artifact_config=artifact_config
        ),
        execute_prompt.s(sas_url, artifact_config, message_id=message_id),
        save_result.s(
            chat_id,
            artifact_version_id,
            sas_url,
            artifact_config,
            message_id=message_id,
        ),
    )()
