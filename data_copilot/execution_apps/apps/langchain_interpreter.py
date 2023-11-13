import uuid
from io import BytesIO
from typing import TYPE_CHECKING, List, Tuple

from data_copilot.execution_apps.base import DataCopilotApp, StaticProperty

if TYPE_CHECKING:
    from data_copilot.execution_apps import helpers
    from data_copilot.backend.artifacts.artifact import CreateArtifactVersionCM
    from data_copilot.backend.schemas.artifacts import Artifact


class LangchainInterpreter(DataCopilotApp):
    @StaticProperty
    def supported_file_types(cls):
        return {
            "text/csv": "csv",
            "application/vnd.ms-excel": "xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        }

    @staticmethod
    def process_data_upload(
        uploaded_files: List, artifact: "Artifact", cm: "CreateArtifactVersionCM"
    ) -> List[Tuple[str, BytesIO]]:
        import json

        import pandas as pd

        file = uploaded_files[0]
        file_type = LangchainInterpreter.supported_file_types.get(
            file.content_type, None
        )

        match file_type:
            case "csv":
                data_frame = pd.read_csv(file.file, sep=None, encoding="utf-8-sig")
            case "xls" | "xlsx":
                data_frame = pd.read_excel(file.file, dtype={"dteday": str})

        if data_frame.empty:
            raise ValueError("Empty file")

        schema = {col: str(data_frame[col].dtype) for col in data_frame.columns}

        file_config = {
            "file_name": file.filename,
            "file_type": file_type,
            "file_schema": schema,
            "rows": data_frame.shape[0],
        }
        artifact_version_config = {
            "artifact_id": str(artifact.id),
            "artifact_version_id": str(cm.uuid),
            "files": [file_config],
        }
        file.file.seek(0)
        files = [
            (
                "config.json",
                json.dumps(artifact_version_config, indent=4),
            ),
            (file.filename, file.file),
        ]
        return files

    @staticmethod
    def execute_message(
        user_prompt: str,
        chat_id: uuid.UUID,
        message_id: uuid.UUID,
        artifact_version_id: uuid.UUID,
        artifact_version_uri: str,
        previous_messages: List[dict],
    ) -> "helpers.Message":
        import json
        import logging
        import os

        from langchain.agents import create_pandas_dataframe_agent
        from langchain.llms import OpenAI
        import openai

        from data_copilot import storage_handler
        from data_copilot.execution_apps import helpers

        message = helpers.Message(helpers.MessageTypes.TEXT, "Answer")

        try:
            artifact_config = json.load(
                storage_handler.read_file(
                    os.path.join(artifact_version_uri, "config.json")
                )
            )
            file_type = artifact_config.get("files", [dict()])[0].get("file_type", "")
            file_name = artifact_config.get("files", [dict()])[0].get("file_name", None)

            if not storage_handler.exists(
                os.path.join(artifact_version_uri, file_name)
            ):
                raise ValueError(
                    f"The artifact version must contain a file named {file_name}",
                )

            dataset = helpers.read_dataset_io(
                os.path.join(artifact_version_uri, file_name), file_type
            )

            if len(dataset.index) == 0:
                raise Exception(
                    f"Wrong '{os.path.join(artifact_version_uri, file_name)}' content"
                )

            agent = create_pandas_dataframe_agent(
                OpenAI(temperature=0), dataset, verbose=False
            )

            answer = agent.run(user_prompt)
            message.add_text(f"{answer}")
        except openai.RateLimitError:
            logging.error(
                "The translation of the user prompt failed due to rate limit error --"
                f"Prompt: {user_prompt} --"
                f"message_id: {message_id}"
            )
            message = helpers.Message(helpers.MessageTypes.ERROR, "Answer")
            message.add_text("Rate limit error from OpenAI API. Please try again later")

        except openai.AuthenticationError:
            logging.error(
                "The translation of the user prompt failed due to authentication "
                f"error -- Prompt: {user_prompt} --"
                f"message_id: {message_id}"
            )
            message.add_text("OpenAI API key is invalid")

        except Exception as e:
            logging.error(
                f"An error occured while translating the user prompt: {e} --"
                f"Prompt: {user_prompt} --"
                f"message_id: {message_id}"
            )

            logging.exception(e)
            message.add_text(
                "An error occured while executing. Please have a look at the logs."
            )
        return message
