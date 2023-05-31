from enum import Enum
from functools import wraps
from typing import Any, Dict

import pandas as pd
import simplejson


def harmonize_column_names(columns):
    return [column.replace(" ", "_").lower() for column in columns]


# Those are copies from the ones in the backend. We can not import them because
# they are not in the same package.
class MessageTypes(str, Enum):
    """Class to represent the different message types."""

    TEXT = "text"
    JSON = "json"
    ERROR = "error"


class ComponentTypes(str, Enum):
    """Class to represent the different component types."""

    TEXT = "text"
    TABLE = "table"
    PLOT_HEATMAP = "plot_heatmap"
    PLOT_HIST = "plot_hist"
    PLOT_BAR = "plot_bar"


class Component:
    """Class to represent a json component."""

    def __init__(self, name: str, comp_type: ComponentTypes) -> None:
        """Initialize the json component.

        Args:
            name (str): The name of the component.
            type (ComponentTypes): The type of the component.
        """
        self.name = name
        self.type = comp_type
        self.data = {}
        self.description = ""
        self.config = {}

    def to_dict(self) -> Dict[str, Any]:
        """Return the json component as a dictionary.

        Returns:
            Dict[str, Any]: The json component as a dictionary.
        """
        return {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "data": stringify_numbers_in_dict(self.data),
            "config": self.config,
        }


def stringify_numbers_in_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Stringify numbers in a dictionary.

    Args:
        data (Dict[str, Any]): The dictionary to stringify.

    Returns:
        Dict[str, Any]: The dictionary with stringified numbers.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = stringify_numbers_in_dict(value)
        elif isinstance(value, (int, float)):
            data[key] = stringify_number(value)
        elif isinstance(value, list):
            data[key] = stringify_numbers_in_list(value)
    return data


def stringify_numbers_in_list(data: list[Any]) -> list[Any]:
    """Stringify numbers in a list.

    Args:
        data (list[Any]): The list to stringify.

    Returns:
        list[Any]: The list with stringified numbers.
    """
    for i, value in enumerate(data):
        if isinstance(value, dict):
            data[i] = stringify_numbers_in_dict(value)
        elif isinstance(value, (int, float)):
            data[i] = stringify_number(value)
        elif isinstance(value, list):
            data[i] = stringify_numbers_in_list(value)
    return data


def stringify_number(value: int | float) -> str:
    """Stringify a number. Use scientific notation if the number is too large.

    Args:
        value (int | float): The number to stringify.

    Returns:
        str: The stringified number.
    """
    if isinstance(value, int) or value.is_integer():
        return str(int(value))
    if value > 1000000 or value < 0.000001:
        return f"{value:.3e}"
    else:
        return f"{value:.3f}"


class Message:
    """Class to represent a json message."""

    def __init__(self, message_type: MessageTypes, method_name: str) -> None:
        """Initialize the json message.

        Args:
            message_type (MessageTypes): The type of the message.
        """
        self.message_type = message_type
        self.method_name = method_name
        self.text_content = ""
        self.components = []

    def add_component(self, component: Component) -> None:
        """Add a component to the json message.

        Args:
            component (Component): The component to add.
        """
        if not self.message_type == MessageTypes.JSON:
            raise ValueError("Cannot add a component to a non-json message.")
        self.components.append(component)

    def add_text(self, text: str) -> None:
        """Add text to the json message.

        Args:
            text (str): The text to add.
        """
        if not self.message_type == MessageTypes.TEXT:
            raise ValueError("Cannot add text to a non-text message.")
        self.text_content += text

    def to_dict(self) -> Dict[str, str]:
        """Return the message as a dictionary with the message type and stringified
        message content.

        Returns:
            Dict[str, str]: The message content and type.
        """
        if self.message_type == "text":
            return {
                "message_type": self.message_type.value,
                "text_content": self.text_content,
            }
        else:
            return {
                "message_type": self.message_type.value,
                "text_content": simplejson.dumps(
                    {
                        "method_name": self.method_name,
                        "components": [
                            component.to_dict() for component in self.components
                        ],
                    },
                    ignore_nan=True,
                ),
            }


def path_processor(func):
    """
    Decorator to process paths
    """

    @wraps(func)
    def wrapper(path, *args, **kwargs):
        if not path:
            raise ValueError("Path cannot be empty")

        if path.startswith("volume://"):
            path = path.replace("volume://", "").replace("//", "/")

        elif path.startswith("file://"):
            path = path.replace("file://", "").replace("//", "/")

        return func(path, *args, **kwargs)

    return wrapper


@path_processor
def read_dataset(sas_url, file_type):
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
