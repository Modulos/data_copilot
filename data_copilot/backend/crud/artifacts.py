import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from data_copilot.backend.schemas import artifacts as artifacts_schema
from data_copilot.db_models import artifacts as artifacts_models


def crud_create_artifact(
    db: Session, artifact: artifacts_schema.CreateArtifact, user_id: uuid.UUID
):
    db_artifact = artifacts_models.Artifact(
        name=artifact.name,
        description=artifact.description,
        user_id=user_id,
        artifact_type=artifact.artifact_type.value,
        status=artifact.status,
    )
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    return db_artifact


def crud_create_artifact_version(
    db: Session, artifact_version: artifacts_schema.CreateArtifactVersion
):
    db_artifact_version = artifacts_models.ArtifactVersion(
        artifact_id=artifact_version.artifact_id,
        artifact_uri=artifact_version.artifact_uri,
        description=artifact_version.description,
        status=artifact_version.status,
    )
    db.add(db_artifact_version)
    db.commit()
    db.refresh(db_artifact_version)
    return db_artifact_version


def crud_update_artifact_version_uri(
    db: Session, artifact_version_id: uuid.UUID, artifact_uri: str
):
    db_artifact_version = crud_get_artifact_version(db, artifact_version_id)
    db_artifact_version.artifact_uri = artifact_uri
    db.commit()
    db.refresh(db_artifact_version)
    return db_artifact_version


def crud_get_artifact(db: Session, artifact_id: uuid.UUID):
    return db.scalars(
        select(artifacts_models.Artifact)
        .filter(artifacts_models.Artifact.id == artifact_id)
        .limit(1)
    ).first()


def crud_get_artifact_with_user_id_if_not_deleted(
    db: Session, artifact_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[artifacts_models.Artifact]:
    """Gets the artifact if it exists, and it is not marked as deleted.

    Args:
        db (Session): Database session.
        artifact_id (UUID): Artifact ID.
        user_id (UUID): User ID.

    Returns (Artifact): The artifact.
    """
    return db.scalars(
        select(artifacts_models.Artifact)
        .filter(artifacts_models.Artifact.id == artifact_id)
        .filter(artifacts_models.Artifact.user_id == user_id)
        .filter(
            artifacts_models.Artifact.status
            != artifacts_schema.ArtifactStatus.deleted.value
        )
        .limit(1)
    ).first()


def crud_update_artifact(
    db: Session, artifact_id: uuid.UUID, update_data: dict
) -> Optional[artifacts_models.Artifact]:
    """Updates artifact's attributes like name, description, etc.

    Args:
        db (Session): Database session.
        artifact_id (UUID): Artifact ID.
        update_data (dict): The updates.

    Returns (Artifact): Updated artifact.
    """
    db_artifact = db.scalars(
        select(artifacts_models.Artifact)
        .filter(artifacts_models.Artifact.id == artifact_id)
        .filter(
            artifacts_models.Artifact.status
            != artifacts_schema.ArtifactStatus.deleted.value
        )
        .limit(1)
    ).first()

    if db_artifact is None:
        return None

    for key, value in update_data.items():
        setattr(db_artifact, key, value)

    db.commit()

    return db_artifact


def crud_soft_delete_artifact(db: Session, artifact_id: uuid.UUID) -> bool:
    """Soft deletes an artifact by changing its status to "deleted".

    Args:
        db (Session): Database session.
        artifact_id (UUID): Artifact's ID.

    Returns (bool): True if the artifact was marked as deleted, False otherwise.
    """
    db_artifact = db.scalars(
        select(artifacts_models.Artifact)
        .filter(artifacts_models.Artifact.id == artifact_id)
        .filter(
            artifacts_models.Artifact.status
            != artifacts_schema.ArtifactStatus.deleted.value
        )
        .limit(1)
    ).first()

    if db_artifact is None:
        return False

    db_artifact.status = artifacts_schema.ArtifactStatus.deleted.value
    db.commit()

    return True


def crud_get_artifact_version(db: Session, artifact_version_id: uuid.UUID):
    return db.scalars(
        select(artifacts_models.ArtifactVersion)
        .filter(artifacts_models.ArtifactVersion.id == artifact_version_id)
        .limit(1)
    ).first()


def crud_get_all_artifacts_by_user_id_and_filters(
    db: Session,
    user_id: uuid.UUID,
    artifact_type: Optional[artifacts_schema.ArtifactTypes],
    status: Optional[artifacts_schema.ArtifactStatus],
) -> list[artifacts_models.Artifact]:
    """Returns all the artifacts owned by the given user and applies filters.

    Args:
        db (Session): Database session.
        user_id (UUID): User's ID.
        artifact_type (ArtifactTypes): Artifact's type.
        status (ArtifactStatus): Artifact's status.

    Returns (list): List of artifacts.
    """
    stmt = select(artifacts_models.Artifact).filter(
        artifacts_models.Artifact.user_id == user_id
    )

    if artifact_type:
        stmt = stmt.filter(
            artifacts_models.Artifact.artifact_type == artifact_type.value
        )

    if status:
        stmt = stmt.filter(artifacts_models.Artifact.status == status.value)

    return db.scalars(stmt).all()


def crud_get_artifact_version_by_artifact_id(
    db: Session, artifact_id: uuid.UUID, limit: int = 1
):
    return db.scalars(
        select(artifacts_models.ArtifactVersion)
        .join(artifacts_models.Artifact)
        .filter(artifacts_models.ArtifactVersion.artifact_id == artifact_id)
        .order_by(artifacts_models.ArtifactVersion.created_at.desc())
        .limit(limit)
    ).all()


def crud_get_artifact_version_by_artifact_id_with_status(
    db: Session,
    artifact_id: uuid.UUID,
    status: str,
    limit: int = 1,
):
    return db.scalars(
        select(artifacts_models.ArtifactVersion)
        .join(artifacts_models.Artifact)
        .filter(artifacts_models.ArtifactVersion.artifact_id == artifact_id)
        .filter(artifacts_models.ArtifactVersion.status == status)
        .order_by(artifacts_models.ArtifactVersion.created_at.desc())
        .limit(limit)
    ).all()


def crud_set_artifact_version_status_to_active(
    db: Session, artifact_version_id: uuid.UUID
):
    db_artifact_version = crud_get_artifact_version(db, artifact_version_id)
    db_artifact_version.status = artifacts_schema.ArtifactVersionStatus.active
    db.commit()
    db.refresh(db_artifact_version)
    return db_artifact_version


def crud_set_artifact_version_status_to_running(
    db: Session, artifact_version_id: uuid.UUID
):
    db_artifact_version = crud_get_artifact_version(db, artifact_version_id)
    db_artifact_version.status = artifacts_schema.ArtifactVersionStatus.running
    db.commit()
    db.refresh(db_artifact_version)
    return db_artifact_version


def crud_set_artifact_version_status_to_failed(
    db: Session, artifact_version_id: uuid.UUID
):
    db_artifact_version = crud_get_artifact_version(db, artifact_version_id)
    db_artifact_version.status = artifacts_schema.ArtifactVersionStatus.failed
    db.commit()
    db.refresh(db_artifact_version)
    return db_artifact_version


def crud_set_artifact_version_status_to_succeeded(
    db: Session, artifact_version_id: uuid.UUID
):
    db_artifact_version = crud_get_artifact_version(db, artifact_version_id)
    db_artifact_version.status = artifacts_schema.ArtifactVersionStatus.succeeded
    db.commit()
    db.refresh(db_artifact_version)
    return db_artifact_version


def crud_set_artifact_version_status_to_deleted(
    db: Session, artifact_version_id: uuid.UUID
):
    db_artifact_version = crud_get_artifact_version(db, artifact_version_id)
    db_artifact_version.status = artifacts_schema.ArtifactVersionStatus.deleted
    db.commit()
    db.refresh(db_artifact_version)
    return db_artifact_version
