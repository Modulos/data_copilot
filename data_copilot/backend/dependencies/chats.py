import uuid

from fastapi import Depends, HTTPException

from data_copilot.backend.crud.chats import (
    crud_get_chat_with_user_id,
    crud_get_message_by_chat_id_and_message_id,
)

from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.authentication import get_current_active_user
from data_copilot.backend.schemas.chats import Chat, Message


async def get_chat_if_user_has_access_dependency(
    chat_id: uuid.UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Chat:
    """Returns the chat if the user has access to it.

    Args:
        chat_id (UUID): Chat's ID.
        db (Session): Database session.
        current_user (User): The user.

    Raises:
        HTTPException: If the chat was not found.

    Returns (Chat): The chat.
    """
    chat = crud_get_chat_with_user_id(db, chat_id, current_user.id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return Chat.from_orm(chat)


async def get_message_if_user_has_access_dependency(
    message_id: uuid.UUID,
    chat: Chat = Depends(get_chat_if_user_has_access_dependency),
    db=Depends(get_db),
) -> Message:
    """Returns the message if it belongs to the chat.

    Args:
        message_id (UUID): Message's ID.
        chat (Chat): The chat.
        db (Session): Database session.

    Raises:
        HTTPException: If the message does not belong to the chat.

    Returns (Message): The message.
    """
    message = crud_get_message_by_chat_id_and_message_id(
        db, chat_id=chat.id, message_id=message_id
    )
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return Message.from_orm(message)
