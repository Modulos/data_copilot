import uuid

from sqlalchemy.orm import Session

from data_copilot.db_models import chats as chats_model


def crud_create_message(
    db: Session,
    chat_id: uuid.UUID,
    artifact_version_id: uuid.UUID | None,
    content: str,
    content_type: str,
):
    # if type(chat_id) is str convert it to uuid
    if type(chat_id) is str:
        chat_id = uuid.UUID(chat_id)

    if type(artifact_version_id) is str:
        artifact_version_id = uuid.UUID(artifact_version_id)

    db_message = chats_model.Message(
        chat_id=chat_id,
        system_generated=True,
        artifact_version_id=artifact_version_id,
        content=content,
        content_type=content_type,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
