import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas import read_excel
import numpy as np

from data_copilot.celery_app.executors import helpers


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
            dataset = pd.read_csv(sas_url, sep=None)
        case "xls" | "xlsx":
            dataset = read_excel(sas_url, dtype={"dteday": str})
        case _:
            raise Exception(f"Unsupported '{file_type}' file type")

    if len(dataset.index) == 0:
        raise Exception(f"Wrong '{sas_url}' content")

    try:
        dataset.columns = helpers.harmonize_column_names(dataset.columns)

        top_3_rows = dataset.head(3).to_dict("list")

    except Exception as e:
        logging.error(e)

    finally:
        pass

    message = helpers.Message(helpers.MessageTypes.JSON, "GETTING_STARTED")

    # Add some table components
    table_component = helpers.Component("Column Names", helpers.ComponentTypes.TABLE)
    table_component.description = "The top 3 rows of the dataset."
    table_component.config = {
        "show_title": True,
        "show_description": True,
        "highlight_columns": [],
    }
    table_component.data = top_3_rows
    message.add_component(table_component)

    # Add some Heatmap components
    correlation = dataset[
        dataset.columns[dataset.dtypes[dataset.columns] != "object"]
    ].corr()
    print("***********\n\nlen(correlation)", correlation)
    if len(correlation) > 0:
        # print(correlation)
        heatmap_component = helpers.Component(
            "Heatmap", helpers.ComponentTypes.PLOT_HEATMAP
        )
        heatmap_component.description = "Correlation between the columns."
        heatmap_component.config = {
            "show_title": True,
            "show_description": True,
            "highlight_columns": [],
        }
        heatmap_component.data = {
            "columns": correlation.columns.tolist(),
            "rows": correlation.index.tolist(),
            "values": correlation.values.tolist(),
        }
        message.add_component(heatmap_component)

    for column in dataset.columns:
        # get unique values sorted by frequency
        unique_values = dataset[column].value_counts().to_dict()

        # get the top 5 values and their frequencies
        top_5 = dict(list(unique_values.items())[:5])
        top_5_values = {str(k): v for k, v in top_5.items()}

        histogram_component = helpers.Component(
            f"Histogram for {column}", helpers.ComponentTypes.PLOT_BAR
        )
        histogram_component.description = f"The top 5 values for {column}."
        histogram_component.config = {
            "show_title": True,
            "show_description": True,
            "highlight_columns": [],
        }
        histogram_component.data = {
            "categories": list(top_5_values.keys()),
            "values": list(top_5_values.values()),
        }
        message.add_component(histogram_component)

    for column in dataset.columns:
        # Check if the column is numeric
        if dataset[column].dtype in ["int64", "float64"]:
            histogram_component = helpers.Component(
                f"Histogram for {column}", helpers.ComponentTypes.PLOT_HIST
            )
            histogram_component.description = f"The Histogram of {column}."
            histogram_component.config = {
                "show_title": True,
                "show_description": True,
                "highlight_columns": [],
            }
            values, bins = np.histogram(dataset[column].values, bins=10, density=True)

            histogram_component.data = {
                "values": values.tolist(),
                "bins": bins.tolist()[:-1],
            }
            message.add_component(histogram_component)

    return message.to_dict()
