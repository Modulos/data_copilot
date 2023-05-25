import logging
import uuid
from typing import Tuple

import openai
import pandas as pd
from celery import Celery, chain
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI

from data_copilot.celery_app.config import Config
from data_copilot.celery_app.crud.chats import crud_create_message
from data_copilot.celery_app.database.psql import SessionLocal, engine
from data_copilot.celery_app.executors import helpers, sql_executor
from data_copilot.celery_app.prompt_interpreter.sql_interpreter import (
    generate_sql_query,
)
from data_copilot.db_models.base import Base

Base.metadata.create_all(bind=engine)


CONFIG = Config()

execution_app = Celery("main", broker=CONFIG.REDIS_URL)


@helpers.path_processor
def read_data(sas_url, file_type):
    match file_type:
        case "csv":
            dataset = pd.read_csv(
                sas_url,
                sep=None,
                encoding="utf-8-sig",
                dtype=object,
                engine="python",
            )
        case "xls" | "xlsx":
            dataset = pd.read_excel(sas_url, dtype={"dteday": str})
        case _:
            raise Exception(f"Unsupported '{file_type}' file type")

    return dataset


# retry 2 times in case of failure
@execution_app.task(
    name="save_result",
    soft_time_limit=3,
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
        message_content, message_type = prompt_result
        db = SessionLocal()
        crud_create_message(
            db,
            chat_id,
            artifact_version_id,
            message_content,
            message_type,
        )
        db.close()
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
        raise e


@execution_app.task(
    name="translating_user_prompt",
    soft_time_limit=60,
    autoretry_for=(TimeLimitExceeded, openai.error.RateLimitError),
    retry_kwargs={"max_retries": 3, "countdown": 30},
)
def translate_user_prompt(
    user_prompt: str,
    message_id: uuid.UUID,
    artifact_config: dict | None = None,
    sas_url: str | None = None,
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
        file_type = artifact_config.get("files", [dict()])[0].get("file_type", "")

        dataset = read_data(sas_url, file_type)

        if len(dataset.index) == 0:
            raise Exception(f"Wrong '{sas_url}' content")

        agent = create_pandas_dataframe_agent(
            OpenAI(temperature=0), dataset, verbose=False
        )

        answer = agent.run(user_prompt)
        message = helpers.Message(helpers.MessageTypes.TEXT, "Answer")
        message.add_text(f"{answer}")
        result = message.to_dict()
        print(result)
        return result["text_content"], result["message_type"]

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
        raise e


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
            user_prompt,
            message_id=message_id,
            artifact_config=artifact_config,
            sas_url=sas_url,
        ),
        save_result.s(
            chat_id,
            artifact_version_id,
            sas_url,
            artifact_config,
            message_id=message_id,
        ),
    )()
