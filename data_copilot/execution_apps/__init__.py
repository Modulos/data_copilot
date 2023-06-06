import enum
import os

from data_copilot.execution_apps.base import DataCopilotApp


class BACKENDS(enum.Enum):
    SQL = "sql"
    LANGCHAIN = "langchain"


STANDARD_BACKEND = BACKENDS.SQL


def get_app() -> DataCopilotApp:
    if os.environ.get("COMPUTE_BACKEND") == BACKENDS.SQL.value:
        from data_copilot.execution_apps.apps.sql_interpreter import SQLInterpreter

        return SQLInterpreter
    elif os.environ.get("COMPUTE_BACKEND") == BACKENDS.LANGCHAIN.value:
        from data_copilot.execution_apps.apps.langchain_interpreter import (
            LangchainInterpreter,
        )

        return LangchainInterpreter
