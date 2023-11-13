from typing import List, Tuple
from io import BytesIO
import uuid

from typing import TYPE_CHECKING

from data_copilot.execution_apps.base import DataCopilotApp, StaticProperty
from data_copilot.execution_apps.helpers import harmonize_column_names

if TYPE_CHECKING:
    from data_copilot.backend.artifacts.artifact import CreateArtifactVersionCM
    from data_copilot.backend.schemas.artifacts import Artifact
    from data_copilot.execution_apps import helpers


def generate_sql_query(prompt, columns):
    from openai import OpenAI

    client = OpenAI()

    columns = harmonize_column_names(columns)
    cols_text = ", ".join(["'" + col + "'" for col in columns])

    rule_1 = (
        "You are an assistant which helps a user to translate a business "
        "question he has about a dataset to a SQL query. You don't execute "
        "the query on the data yourself. You are only allowed to write SQL "
        "queries that are compatible with SQLite."
    )
    prompt_1 = (
        "Please answer if the following user question can be "
        "answered with an sql query and no additional text: "
        f"{prompt}\n"
        "The table is called: df \n"
        f"The column name of the data are: {cols_text}"
        "Answer [yes/no]: "
    )

    messages = [
        {"role": "system", "content": rule_1},
        {"role": "user", "content": prompt_1},
    ]

    response = (
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1,
        )
        .choices[0]
        .message.content
    )

    if response.lower() in ("y", "yes"):
        response_type = "SQL"

        rule_2 = (
            "You are an assistant which helps a user to translate a "
            "business question he has about a dataset to a SQL query. "
            "You don't execute the query on the data yourself. You are "
            "only allowed to write SQL queries that are compatible with "
            "SQLite."
        )
        prompt_2 = (
            "Please answer the following user question with an sql query "
            "and no additional text: "
            f"{prompt}\n"
            "The table is called: df \n"
            f"The column name of the data are: {cols_text}"
            "SQLite Query:"
        )
        messages = [
            {"role": "system", "content": rule_2},
            {"role": "user", "content": prompt_2},
        ]

        response = (
            client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages, temperature=0.0
            )
            .choices[0]
            .message.content
        )

    elif response.lower() in ("n", "no"):
        response_type = "TEXT"
        rule_3 = (
            "You are an assistant which helps a user to translate a "
            "business question he has about a dataset to a SQL query. "
            "You don't execute the query on the data yourself. You are "
            "only allowed to write SQL queries that are compatible with "
            "SQLite."
        )
        prompt_3 = (
            "Please explain why it is not possible to translate the "
            "following question to sql: "
            f"{prompt}\n"
            "The table is called: df \n"
            f"The column name of the data are: {cols_text}"
            "Your Answer:"
        )

        messages = [
            {"role": "system", "content": rule_3},
            {"role": "user", "content": prompt_3},
        ]

        response = (
            client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
            .choices[0]
            .message.content
        )

    else:
        response_type = "TEXT"

    return (response_type, response)


class SQLInterpreter(DataCopilotApp):
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
        import pandas as pd
        import json

        file = uploaded_files[0]
        file_type = SQLInterpreter.supported_file_types.get(file.content_type, None)

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
        import os
        from data_copilot import storage_handler
        import logging
        from data_copilot.execution_apps import helpers
        import openai
        import pandas as pd
        from sqlalchemy import create_engine, text

        try:
            artifact_config = json.load(
                storage_handler.read_file(
                    os.path.join(artifact_version_uri, "config.json")
                )
            )
            file_type = artifact_config.get("files", [dict()])[0].get("file_type", "")
            file_name = artifact_config.get("files", [dict()])[0].get("file_name", None)
            schema = artifact_config.get("files", [dict()])[0].get("file_schema", {})

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

            query = generate_sql_query(user_prompt, schema.keys())

            if query[0] == "TEXT":
                message = helpers.Message(helpers.MessageTypes.TEXT, "Answer")
                message.add_text(query[1])

            else:  # query[0] == "SQL"
                engine = create_engine("sqlite:///:memory:")
                # Write the DataFrame to the SQL table

                dataset.columns = helpers.harmonize_column_names(dataset.columns)

                dataset.to_sql("df", engine, if_exists="replace", index=False)

                # Your query variable
                query = text(query[1].replace("```", "").strip())

                # Create a connection and execute the query
                with engine.connect() as connection:
                    result_df = pd.read_sql_query(query, connection)

                    # limit the result to 100 rows
                    result_df = result_df.head(100)

                engine.dispose()

                message = helpers.Message(helpers.MessageTypes.JSON, "SQL")
                table_component = helpers.Component(
                    "Column Names", helpers.ComponentTypes.TABLE
                )
                table_component.description = "The Result of your SQL Query"
                table_component.config = {
                    "show_title": True,
                    "show_description": False,
                    "highlight_columns": [],
                }
                table_component.data = result_df.to_dict("list")
                message.add_component(table_component)

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
