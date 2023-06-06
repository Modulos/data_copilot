import abc
import uuid
from io import BytesIO
from typing import List, Tuple

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data_copilot.backend.artifacts.artifact import CreateArtifactVersionCM
    from data_copilot.backend.schemas.artifacts import Artifact
    from data_copilot.execution_apps import helpers


class StaticProperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class DataCopilotApp(abc.ABC):
    @StaticProperty
    @abc.abstractmethod
    def supported_file_types(cls):
        pass

    @staticmethod
    @abc.abstractmethod
    def process_data_upload(
        uploaded_files: List, artifact: "Artifact", cm: "CreateArtifactVersionCM"
    ) -> List[Tuple[str, BytesIO]]:
        pass

    @staticmethod
    @abc.abstractmethod
    def execute_message(
        user_prompt: str,
        chat_id: uuid.UUID,
        message_id: uuid.UUID,
        artifact_version_id: uuid.UUID,
        artifact_version_uri: str,
        previous_messages: List[dict],
    ) -> "helpers.Message":
        pass
