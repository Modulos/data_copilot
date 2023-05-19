import logging
from functools import wraps
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas import read_excel
from sqlalchemy import create_engine, text

from celery_app.executors import helpers


@helpers.path_processor
def run(
    sas_url: str,
    schema: Dict[str, Any],
    file_type: str,
    sql_query: str,
    columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Execute the command and return the correct json response.

    Args:
        sas_url (str): The path to the dataset to operate on.
        schema (Dict[str, Any]): The schema of the dataset.
        sql_query (str): The SQL query to execute.
        columns (Optional[List[str]], optional): The columns to execute the
            command on. Defaults to None.
    """

    match file_type:
        case "csv":
            dataset = pd.read_csv(sas_url, sep=None, dtype=object)
        case "xls" | "xlsx":
            dataset = read_excel(sas_url, dtype={"dteday": str})
        case _:
            raise Exception(f"Unsupported '{file_type}' file type")

    if len(dataset.index) == 0:
        raise Exception(f"Wrong '{sas_url}' content")

    engine = create_engine("sqlite:///:memory:")
    try:
        # Write the DataFrame to the SQL table

        dataset.columns = helpers.harmonize_column_names(dataset.columns)

        dataset.to_sql("df", engine, if_exists="replace", index=False)

        # Your query variable
        query = text(sql_query)

        # Create a connection and execute the query
        with engine.connect() as connection:
            result_df = pd.read_sql_query(query, connection)

            # limit the result to 100 rows
            result_df = result_df.head(100)

    except Exception as e:
        logging.error(e)

    finally:
        engine.dispose()

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
