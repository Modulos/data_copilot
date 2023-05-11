import logging
from functools import wraps
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas import read_excel
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

from celery_app.config import Config
from celery_app.executors import helpers

custom_locations = {"volume": "shared-fs/"}

CONFIG = Config()


def path_processor(func):
    """
    Decorator to process paths
    """

    @wraps(func)
    def wrapper(path, *args, **kwargs):
        if not path:
            raise ValueError("Path cannot be empty")

        if path.startswith("volume://"):
            path = path.replace("volume://", custom_locations["volume"]).replace(
                "//", "/"
            )

        return func(path, *args, **kwargs)

    return wrapper


@path_processor
def run(
    sas_url: str,
    schema: Dict[str, Any],
    file_type: str,
    prompt: str,
    columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Execute the databits command and return the correct json response.

    Args:
        sas_url (str): The path to the dataset to operate on.
        schema (Dict[str, Any]): The schema of the dataset.
        prompot (str): The prompt to execute.
        columns (Optional[List[str]], optional): The columns to execute the
            command on. Defaults to None.
    """
    # Set up the arguments passed to databits.

    match file_type:
        case "csv":
            dataset = pd.read_csv(sas_url, sep=None, dtype=object)
        case "xls" | "xlsx":
            dataset = read_excel(sas_url, dtype={"dteday": str})
        case _:
            raise Exception(f"Unsupported '{file_type}' file type")

    if len(dataset.index) == 0:
        raise Exception(f"Wrong '{sas_url}' content")

    llm = OpenAI(api_token=CONFIG.OPENAI_API_KEY)

    pandas_ai = PandasAI(llm, conversational=False)
    result_df = pandas_ai.run(dataset, prompt=prompt)

    print(result_df)

    message = helpers.Message(helpers.MessageTypes.JSON, "SQL")
    table_component = helpers.Component("Column Names", helpers.ComponentTypes.TABLE)
    table_component.description = "The Result of your SQL Query"
    table_component.config = {
        "show_title": True,
        "show_description": True,
        "highlight_columns": [],
    }
    table_component.data = result_df.to_dict("list")
    message.add_component(table_component)

    return message.to_dict()
