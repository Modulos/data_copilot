import logging
import uuid
from typing import Tuple

import openai
from celery import Celery, chain
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
from openai import error

from data_copilot.celery_app.config import Config
from data_copilot.celery_app.crud.chats import crud_create_message
from data_copilot.celery_app.database.psql import SessionLocal, engine
from data_copilot.celery_app.executors import sql_executor
from data_copilot.celery_app.prompt_interpreter.sql_interpreter import (
    generate_sql_query,
)
from data_copilot.db_models.base import Base

Base.metadata.create_all(bind=engine)


CONFIG = Config()

execution_app = Celery("main", broker=CONFIG.CELERY_BROKER_URL)


# retry 2 times in case of failure
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


@execution_app.task(name="execute_prompt", soft_time_limit=30)
def execute_prompt(
    query: Tuple[str, str],
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
    query_type, query_content = query

    if query_type == "error":
        return query
    try:
        schema = artifact_config.get("files", [dict()])[0].get("file_schema", {})
        file_type = artifact_config.get("files", [dict()])[0].get("file_type", "")

        message = sql_executor.run(
            sas_url, schema, file_type, query_content, schema.keys()
        )

        return message["message_type"], message["text_content"]
    except SoftTimeLimitExceeded:
        logging.error(
            "The execution of the prompt timed out --" f"message_id: {message_id} --"
        )
        return "error", "The execution of the prompt timed out"

    except Exception as e:
        logging.error(
            f"An error occurred while executing method: {e} -- "
            f"message_id: {message_id}"
        )
        logging.exception(e)
        return "error", "An error occurred while executing method"


@execution_app.task(
    name="translating_user_prompt",
    soft_time_limit=60,
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
        schema = artifact_config.get("files", [dict()])[0].get("file_schema", {})
        query = generate_sql_query(user_prompt, schema.keys())
        return "query", query

    except SoftTimeLimitExceeded:
        logging.error(
            "The translation of the user prompt timed out --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )
        raise TimeLimitExceeded()

    except error.AuthenticationError:
        return "error", "OpenAI API key is invalid"

    except Exception as e:
        logging.error(
            f"An error occured while translating the user prompt: {e} --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )
        logging.exception(e)
        return "error", "An error occured while translating the user prompt"


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
