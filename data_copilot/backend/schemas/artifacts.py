import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import field_validator, ConfigDict, BaseModel


class ArtifactVersionStatus(str, Enum):
    latest = "latest"
    active = "active"
    running = "running"
    failed = "failed"
    succeeded = "succeeded"
    created = "created"
    deleted = "deleted"


class ArtifactStatus(str, Enum):
    active = "active"
    deleted = "deleted"


class ArtifactTypes(str, Enum):
    dataset = "dataset"
    model = "model"
    pipeline = "config"


class ArtifactVersion(BaseModel):
    id: uuid.UUID
    artifact_uri: str
    artifact_id: uuid.UUID
    description: str = ""
    created_at: datetime
    status: ArtifactVersionStatus = ArtifactVersionStatus.active
    model_config = ConfigDict(from_attributes=True)


class ArtifactVersionFiles(ArtifactVersion):
    files: list[str]
    model_config = ConfigDict(from_attributes=True)


class Artifact(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    artifact_type: ArtifactTypes
    description: str = ""
    created_at: datetime
    status: ArtifactStatus = ArtifactStatus.active
    model_config = ConfigDict(from_attributes=True)


class UpdateArtifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_be_not_none(cls, v):
        if v is None:
            raise ValueError("must be not None")

        return v

    @field_validator("description")
    @classmethod
    def description_must_be_not_none(cls, v):
        if v is None:
            raise ValueError("must be not None")

        return v


class CreateArtifactVersion(BaseModel):
    artifact_uri: str
    artifact_id: uuid.UUID
    description: str = ""
    status: ArtifactVersionStatus = ArtifactVersionStatus.active


class CreateArtifactBase(BaseModel):
    name: str
    artifact_type: ArtifactTypes
    description: str = ""


class CreateArtifact(CreateArtifactBase):
    status: ArtifactStatus = ArtifactStatus.active


class ArtifactVersionTableFile(BaseModel):
    file_name: str
    data_schema: str


class ArtifactVersionConfiguration(BaseModel):
    artifact_id: uuid.UUID
    artifact_version_id: uuid.UUID
    artifact_version_uri: str
    artifact_type: ArtifactTypes
    artifact_version_files: List[ArtifactVersionTableFile]
