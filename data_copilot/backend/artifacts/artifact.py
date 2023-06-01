import os

from sqlalchemy.orm import Session

from data_copilot.backend.config import Config
from data_copilot.backend.crud.artifacts import (
    crud_create_artifact_version,
    crud_set_artifact_version_status_to_failed,
    crud_set_artifact_version_status_to_running,
    crud_set_artifact_version_status_to_succeeded,
    crud_update_artifact_version_uri,
)
from data_copilot.backend.schemas.artifacts import (
    ArtifactVersionStatus,
    CreateArtifactVersion,
)
from data_copilot.storage_handler import write_file

CONFIG = Config()


class CreateArtifactVersionCM:
    def __init__(self, artifact_id: int, db: Session):
        self.db = db
        self.artifact_id = artifact_id
        self.uuid = None
        self.uri = None
        pass

    def __enter__(self):
        self.artifact_version = crud_create_artifact_version(
            self.db,
            CreateArtifactVersion(
                artifact_id=self.artifact_id,
                artifact_uri="",
                status=ArtifactVersionStatus.created,
            ),
        )
        self.uri = os.path.join(
            CONFIG.STORAGE_BACKEND,
            str(self.artifact_id),
            str(self.artifact_version.id),
        )
        self.uuid = self.artifact_version.id
        crud_update_artifact_version_uri(self.db, self.artifact_version.id, self.uri)
        crud_set_artifact_version_status_to_running(self.db, self.artifact_version.id)
        return self

    def write(self, file_name: str, file_content: bytes):
        write_file(os.path.join(self.uri, file_name), file_content)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            crud_set_artifact_version_status_to_failed(
                self.db, self.artifact_version.id
            )
            # write exec_val to logging
        else:
            crud_set_artifact_version_status_to_succeeded(
                self.db, self.artifact_version.id
            )

        self.db.close()
