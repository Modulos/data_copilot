import json
import logging
import os
from typing import Optional

import pandas as pd
from fastapi import Depends, HTTPException, UploadFile, routing

from data_copilot.backend.artifacts.artifact import CreateArtifactVersionCM
from data_copilot.backend.config import Config
from data_copilot.backend.crud.artifacts import (
    crud_create_artifact,
    crud_get_all_artifacts_by_user_id_and_filters,
    crud_get_artifact_version,
    crud_get_artifact_version_by_artifact_id,
    crud_get_artifact_version_by_artifact_id_with_status,
    crud_soft_delete_artifact,
    crud_update_artifact,
)
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.artifacts import (
    check_if_artifact_version_belongs_to_artifact,
    get_artifact_if_user_has_access_and_not_deleted_dependency,
    get_artifact_version_dependency,
)
from data_copilot.backend.dependencies.authentication import get_current_active_user
from data_copilot.backend.schemas.artifacts import (
    Artifact,
    ArtifactStatus,
    ArtifactTypes,
    ArtifactVersion,
    ArtifactVersionFiles,
    ArtifactVersionStatus,
    CreateArtifact,
    CreateArtifactBase,
    UpdateArtifact,
)
from data_copilot.backend.schemas.authentication import User
from data_copilot.storage_handler import get_signed_download_url, list_files

artifacts_router = routing.APIRouter(prefix="/artifacts")

CONFIG = Config()


@artifacts_router.get("/", status_code=200, response_model=list[Artifact])
async def get_artifacts(
    current_user: User = Depends(get_current_active_user),
    artifact_type: Optional[ArtifactTypes] = None,
    status: Optional[ArtifactStatus] = None,
    db=Depends(get_db),
):
    """
    List all the artifacts owned by the current user and apply filters if any.

    Args:
        current_user (User): The current user
        artifact_type (ArtifactTypes): The type of the artifact to filter on.
        status (ArtifactStatus): Artifact's status
        db (Session): Database session.

    Returns:
        list[Artifact]: List of artifacts.
    """
    return crud_get_all_artifacts_by_user_id_and_filters(
        db, user_id=current_user.id, artifact_type=artifact_type, status=status
    )


@artifacts_router.post("/", status_code=201, response_model=Artifact)
async def post_artifact(
    artifact: CreateArtifactBase,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """
    Create a new artifact of a given type. The artifact is
    created by the current user. Only the current user can access
    the artifact. The artifact is created with status "active".

    Args:
        artifact (CreateArtifactBase): The artifact to be created
        current_user (User): The current user
        db (Session): Database session.

    Returns:
        Artifact: The created artifact
    """
    artifact = CreateArtifact(
        status=ArtifactStatus.active,
        **artifact.dict(),
    )
    return crud_create_artifact(db, artifact, user_id=current_user.id)


@artifacts_router.get(
    "/{artifact_id}",
    status_code=200,
    response_model=Artifact,
)
async def get_artifacts_id_artifactid(
    artifact: Artifact = Depends(
        get_artifact_if_user_has_access_and_not_deleted_dependency
    ),
):
    """
    Get an artifact by id. Only the current user can access the artifact.

    Args:
        artifact (Artifact): The artifact

    Returns:
        Artifact: The artifact.
    """
    return artifact


@artifacts_router.patch(
    "/{artifact_id}",
    response_model=Artifact,
)
async def patch_artifact_id_artifactid(
    artifact_update: UpdateArtifact,
    artifact: Artifact = Depends(
        get_artifact_if_user_has_access_and_not_deleted_dependency
    ),
    db=Depends(get_db),
):
    """Updates artifact's attributes like name, description, etc.

    Args:
        artifact_update (UpdateArtifact): The updates.
        artifact (Artifact): The artifact to be updated.
        db (Session): Database session.

    Raises:
        HTTPException: If the artifact was not found, or it has status "deleted".

    Returns (Session): Updated artifact.
    """
    update_data = artifact_update.dict(exclude_unset=True)
    updated_artifact = crud_update_artifact(db, artifact.id, update_data)

    if updated_artifact is None:
        raise HTTPException(
            status_code=404,
            detail="The artifact was not found.",
        )

    return updated_artifact


@artifacts_router.delete(
    "/{artifact_id}",
    status_code=204,
)
async def delete_artifact_id_artifactid(
    artifact: Artifact = Depends(
        get_artifact_if_user_has_access_and_not_deleted_dependency
    ),
    db=Depends(get_db),
):
    """Soft deletes the artifact with the given ID.

    Args:
        artifact (Artifact): The artifact.
        db (Session): Database session.

    Raises:
        HTTPException: If the artifact was not found.
    """
    deleted = crud_soft_delete_artifact(db, artifact.id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="The artifact was not found.",
        )


@artifacts_router.get(
    "/{artifact_id}/versions",
    status_code=200,
    response_model=list[ArtifactVersion],
)
async def get_artifacts_id_artifactid_versions(
    artifact: Artifact = Depends(
        get_artifact_if_user_has_access_and_not_deleted_dependency
    ),
    status: ArtifactVersionStatus = ArtifactVersionStatus.latest,
    limit: int = 1,
    db=Depends(get_db),
):
    """
    Get a list of artifact versions for a given artifact. The list is ordered by
    creation date. The list can be filtered by status. The default status is "latest",
    which returns the latest artifact version ignoring the status. Only the current user
    can access the artifact.

    Args:
        artifact (Artifact): The artifact
        status (ArtifactVersionStatus): The status of the artifact version
        limit (int): The number of artifact versions to return. Default is 1.
        db (Session): Database session.

    Returns:
        list[ArtifactVersion]: The list of artifact versions
    """
    if status.value == "latest":
        artifact_version = crud_get_artifact_version_by_artifact_id(
            db, artifact.id, limit
        )
    else:
        artifact_version = crud_get_artifact_version_by_artifact_id_with_status(
            db, artifact.id, status.value, limit
        )

    if artifact_version is None:
        raise routing.HTTPException(
            status_code=404, detail="Artifact Version not found"
        )

    return artifact_version


@artifacts_router.get(
    "/{artifact_id}/versions/{artifact_version_id}",
    status_code=200,
    response_model=ArtifactVersionFiles,
)
async def get_artifacts_id_artifactid_versions_artifactversionid(
    artifact: Artifact = Depends(
        get_artifact_if_user_has_access_and_not_deleted_dependency
    ),
    artifact_version: ArtifactVersion = Depends(get_artifact_version_dependency),
):
    """
    Get an artifact version by artifact and artifact version
    id. Only the current user can access the artifact.

    Args:
        artifact (Artifact): The artifact
        artifact_version (ArtifactVersion): The artifact version

    Returns:
        ArtifactVersionFiles: The artifact version with the list of files

    """
    await check_if_artifact_version_belongs_to_artifact(artifact, artifact_version)
    files = list_files(artifact_version.artifact_uri)
    files = [os.path.basename(file) for file in files]

    return ArtifactVersionFiles(**artifact_version.__dict__, files=files)


@artifacts_router.get(
    "/{artifact_id}/versions/{artifact_version_id}/files/{file_name}",
    status_code=200,
)
async def get_artifacts_id_artifactid_versions_artifactversionid_files_filename(
    file_name: str,
    artifact: Artifact = Depends(
        get_artifact_if_user_has_access_and_not_deleted_dependency
    ),
    artifact_version: ArtifactVersion = Depends(get_artifact_version_dependency),
):
    """
    Get the list of files in the given artifact version. Only the current
    user can access the artifact and the artifact version.

    Args:
        file_name (str): The name of the file
        artifact (Artifact): The artifact
        artifact_version (ArtifactVersion): The artifact version

    Returns:
        str: The SAS URL for the file

    """
    await check_if_artifact_version_belongs_to_artifact(artifact, artifact_version)

    files = list_files(artifact_version.artifact_uri)

    files = [os.path.basename(file) for file in files]

    if file_name not in files:
        raise routing.HTTPException(status_code=404, detail="File not found")

    return get_signed_download_url(
        os.path.join(artifact_version.artifact_uri, file_name)
    )


@artifacts_router.post(
    "/{artifact_id}/versions",
    status_code=201,
    response_model=ArtifactVersion,
)
async def post_artifacts_id_artifactid_versions(
    file: UploadFile,
    artifact: Artifact = Depends(
        get_artifact_if_user_has_access_and_not_deleted_dependency
    ),
    db=Depends(get_db),
):
    """
    Upload a new artifact version for a given artifact. Only the
    current user can access the artifact.
    The artifact version is created with status "succeeded".

    Args:
        file (UploadFile): The file to upload
        artifact (Artifact): The artifact
        db (Session): Database session.

    Returns:
        ArtifactVersion: The artifact version
    """
    if artifact.artifact_type != ArtifactTypes.dataset:
        raise routing.HTTPException(
            status_code=400, detail="Only dataset artifact versions can be uploaded"
        )

    if file.content_type not in CONFIG.ALLOWED_ARTIFACTS_CONTENT_TYPES.keys():
        raise routing.HTTPException(
            status_code=415, detail=f"File format '{file.content_type}' not allowed"
        )

    try:
        file_type = CONFIG.ALLOWED_ARTIFACTS_CONTENT_TYPES[file.content_type]
        match file_type:
            case "csv":
                data_frame = pd.read_csv(file.file, sep=None, encoding="utf-8-sig")
            case "xls" | "xlsx":
                data_frame = pd.read_excel(await file.read(), dtype={"dteday": str})

        if data_frame.empty:
            raise routing.HTTPException(
                status_code=400, detail=f"Wrong '{file.file}'content"
            )

    except Exception as e:
        logging.error(e)
        raise routing.HTTPException(
            status_code=500, detail=f"Loading '{file.content_type}' failed"
        )
    schema = {col: str(data_frame[col].dtype) for col in data_frame.columns}
    file_config = {
        "file_name": file.filename,
        "file_type": file_type,
        "file_schema": schema,
        "rows": data_frame.shape[0],
    }
    file.file.seek(0)
    with CreateArtifactVersionCM(artifact.id, db) as cm:
        cm.write(file.filename, file.file)
        artifact_version_config = {
            "artifact_id": str(artifact.id),
            "artifact_version_id": str(cm.uuid),
            "files": [file_config],
        }
        cm.write("config.json", json.dumps(artifact_version_config, indent=4))
        uuid = cm.uuid

    return crud_get_artifact_version(db, uuid)
