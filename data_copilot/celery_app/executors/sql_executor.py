import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from data_copilot.celery_app.executors import helpers


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

    dataset = helpers.read_dataset(sas_url, file_type)

    if len(dataset.index) == 0:
        raise Exception(f"Wrong '{sas_url}' content")

    if sql_query[0] == "TEXT":
        message = helpers.Message(helpers.MessageTypes.TEXT, "SQL")
        message.add_text(sql_query[1])
        return message.to_dict()

    engine = create_engine("sqlite:///:memory:")
    try:
        # Write the DataFrame to the SQL table

        dataset.columns = helpers.harmonize_column_names(dataset.columns)

        dataset.to_sql("df", engine, if_exists="replace", index=False)

        # Your query variable
        query = text(sql_query[1].replace("```", "").strip())

        # Create a connection and execute the query
        with engine.connect() as connection:
            result_df = pd.read_sql_query(query, connection)

            # limit the result to 100 rows
            result_df = result_df.head(100)

    except Exception as e:
        logging.error(e)
        raise e

    finally:
        engine.dispose()

    message = helpers.Message(helpers.MessageTypes.JSON, "SQL")
    table_component = helpers.Component("Column Names", helpers.ComponentTypes.TABLE)
    table_component.description = "The Result of your SQL Query"
    table_component.config = {
        "show_title": True,
        "show_description": False,
        "highlight_columns": [],
    }
    table_component.data = result_df.to_dict("list")
    message.add_component(table_component)

    return message.to_dict()
