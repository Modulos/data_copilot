import uuid

from fastapi import Depends, HTTPException

from data_copilot.backend.crud.artifacts import (
    crud_get_artifact,
    crud_get_artifact_version,
    crud_get_artifact_with_user_id_if_not_deleted,
)
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.authentication import get_current_active_user
from data_copilot.backend.schemas.artifacts import (
    Artifact,
    ArtifactVersion,
    ArtifactStatus,
)
from data_copilot.backend.schemas.authentication import User


async def get_artifact_dependency(
    artifact_id: uuid.UUID, db=Depends(get_db)
) -> Artifact:
    """Returns the artifact based on the artifact ID.

    Args:
        artifact_id (UUID): Artifact ID.
        db (Session): Database session.

    Raises:
        HTTPException: If the artifact was not found.

    Returns (Artifact): The artifact.
    """
    artifact = crud_get_artifact(db, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return Artifact.from_orm(artifact)


async def get_artifact_if_user_has_access_and_not_deleted_dependency(
    artifact_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> Artifact:
    """Returns the artifact if it is not deleted.

    Args:
        artifact_id (UUID): Artifact ID.
        current_user (User): The current user.
        db (Session): Database session.

    Raises:
        HTTPException: If the artifact was not found, or it was deleted.

    Returns (Artifact): The artifact.
    """
    artifact = crud_get_artifact_with_user_id_if_not_deleted(
        db, artifact_id, current_user.id
    )

    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return Artifact.from_orm(artifact)


async def get_artifact_version_dependency(
    artifact_version_id: uuid.UUID, db=Depends(get_db)
) -> ArtifactVersion:
    """Returns the artifact version based on the artifact version ID.

    Args:
        artifact_version_id (UUID): Artifact version ID.
        db (Session): Database session.

    Raises:
        HTTPException: If the artifact version was not found.

    Returns (ArtifactVersion): The artifact version.
    """
    artifact_version = crud_get_artifact_version(db, artifact_version_id)
    if artifact_version is None:
        raise HTTPException(status_code=404, detail="Artifact Version not found")
    return ArtifactVersion.from_orm(artifact_version)


async def get_artifact_from_artifact_version_dependency(
    artifact_version: ArtifactVersion = Depends(get_artifact_version_dependency),
    db=Depends(get_db),
) -> Artifact:
    """Returns the artifact based on the artifact version.

    Args:
        artifact_version (ArtifactVersion): Artifact version.
        db (Session): Database session.

    Raises:
        HTTPException: If the artifact was not found.

    Returns (Artifact): The artifact.
    """
    artifact = crud_get_artifact(db, artifact_version.artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return Artifact.from_orm(artifact)


async def check_if_artifact_version_belongs_to_artifact(
    artifact: Artifact, artifact_version: ArtifactVersion
) -> None:
    """Checks if artifact version belongs to an artifact.

    Args:
        artifact (Artifact): The artifact.
        artifact_version (ArtifactVersion): The artifact version.

    Raises:
        HTTPException: If the artifact version does not belong to the artifact.
    """
    if artifact_version.artifact_id != artifact.id:
        raise HTTPException(
            status_code=404, detail="Artifact version not found for given artifact"
        )
    return None


async def check_if_user_has_access_to_artifact(
    artifact: Artifact = Depends(get_artifact_dependency),
    current_user: User = Depends(get_current_active_user),
) -> bool:
    """Checks if user has access to an artifact.

    Args:
        artifact (Artifact): The artifact.
        current_user (User): The user.

    Raises:
        HTTPException: If the user does not have access to the artifact.

    Returns (bool): True if the user has access to the artifact.
    """
    if current_user.id != artifact.user_id:
        raise HTTPException(status_code=400, detail="Access denied")
    return True


async def check_if_artifact_is_active(
    artifact: Artifact = Depends(get_artifact_dependency),
) -> bool:
    """Checks if artifact is active.

    Args:
        artifact (Artifact): The artifact.

    Raises:
        HTTPException: If the artifact is not active.

    Returns (bool): True if the artifact is active.
    """
    if artifact.status != ArtifactStatus.active:
        raise HTTPException(status_code=404, detail="Artifact has been deleted")
    return True
