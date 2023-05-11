import uuid

from sqlalchemy.orm import Session

from db_models import chats as chats_model


def crud_create_message(
    db: Session,
    chat_id: uuid.UUID,
    sender_id: uuid.UUID,
    system_generated: bool,
    artifact_version_id: uuid.UUID | None,
    content: str,
    content_type: str,
):
    db_message = chats_model.Message(
        chat_id=chat_id,
        sender_id=sender_id,
        system_generated=system_generated,
        artifact_version_id=artifact_version_id,
        content=content,
        content_type=content_type,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
