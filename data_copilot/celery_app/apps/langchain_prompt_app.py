import logging
import uuid
from typing import Tuple

import openai
from celery import Celery, chain
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI
from openai import error

from data_copilot.celery_app.config import Config
from data_copilot.celery_app.crud.chats import crud_create_message
from data_copilot.celery_app.database.psql import SessionLocal, engine
from data_copilot.celery_app.executors import helpers
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
        prompt_result (Tuple[str, str]): _description_
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
) -> Tuple[str, str]:
    """Translate user prompt into method to be called

    Args:
        user_prompt (str): Prompt passed from the user message to be executed.
        message_id (uuid.UUID): message id of the prompt.
        artifact_config (dict):

    Returns:
        Tuple[str, str]: Tuple of message type and message content.
    """
    try:
        # schema = artifact_config.get("files", [dict()])[0].get("file_schema", {})
        file_type = artifact_config.get("files", [dict()])[0].get("file_type", "")

        dataset = helpers.read_dataset(sas_url, file_type)

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
        return result["message_type"], result["text_content"]

    except SoftTimeLimitExceeded:
        logging.error(
            "The translation of the user prompt timed out --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )
        raise TimeLimitExceeded()

    except error.RateLimitError:
        logging.error(
            "The translation of the user prompt failed due to rate limit error --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )
        return "error", "Rate limit error from OpenAI API. Please try again later"

    except error.AuthenticationError:
        logging.error(
            "The translation of the user prompt failed due to authentication error --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )
        return "error", "OpenAI API key is invalid"

    except Exception as e:
        logging.error(
            f"An error occured while translating the user prompt: {e} --"
            f"Prompt: {user_prompt} --"
            f"message_id: {message_id}"
        )

        logging.exception(e)
        return (
            "error",
            "An error occured while executing. Please have a look at the logs.",
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
