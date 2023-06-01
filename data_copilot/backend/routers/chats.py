import asyncio
import json
import os
import time

from fastapi import Depends, HTTPException, routing

from data_copilot.backend.celery import execution_app
from data_copilot.backend.config import Config
from data_copilot.backend.crud.chats import (
    crud_create_chat,
    crud_create_chat_membership,
    crud_create_message,
    crud_get_all_chats_with_user_id,
    crud_get_messages_by_chat_id_sorted_desc,
    crud_get_messages_total_number_by_chat_id_and_filters,
    crud_set_chat_membership_user_id_inactive,
    crud_set_chat_membershipt_user_id_chat_id_inactive,
    crud_update_chat,
)
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.artifacts import (
    check_if_user_has_access_to_artifact,
    check_if_artifact_is_active,
    get_artifact_from_artifact_version_dependency,
    get_artifact_version_dependency,
)
from data_copilot.backend.dependencies.authentication import get_current_active_user
from data_copilot.backend.dependencies.chats import (
    get_chat_if_user_has_access_dependency,
    get_message_if_user_has_access_dependency,
)
from data_copilot.backend.schemas.artifacts import Artifact, ArtifactVersion
from data_copilot.backend.schemas.authentication import User
from data_copilot.backend.schemas.chats import (
    Chat,
    CreateChat,
    CreateChatCRUD,
    CreateChatMembershipCRUD,
    CreateMessage,
    CreateMessageCRUD,
    Message,
    MessagesResponse,
    MessagesResponseMetadata,
    RequestOptions,
    UpdateChat,
    parse_chat_message,
)
from data_copilot.storage_handler.functions import (
    exists,
    get_signed_download_url,
    read_file,
)

CONFIG = Config()

chats_router = routing.APIRouter(prefix="/chats")


@chats_router.get("", response_model=list[Chat])
async def get_chats(
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """
    Returns all the chats of the current user
    """
    return crud_get_all_chats_with_user_id(db, current_user.id)


@chats_router.post(
    "",
    response_model=Chat,
    dependencies=[Depends(check_if_user_has_access_to_artifact)],
)
async def create_chat(
    current_user: User = Depends(get_current_active_user),
    chat: CreateChat = Depends(),
    db=Depends(get_db),
):
    """
    Creates a new chat

    Args:
        chat (CreateChat): The chat to be created

    Returns:
        Chat: The created chat
    """
    create_chat = CreateChatCRUD(**chat.__dict__, owner_id=current_user.id)
    db_chat = crud_create_chat(db, create_chat)

    create_chat_membership = CreateChatMembershipCRUD(
        chat_id=db_chat.id, member_id=current_user.id, is_active=True
    )
    crud_create_chat_membership(db, create_chat_membership)

    return db_chat


@chats_router.get("/{chat_id}", response_model=Chat)
async def get_chat_chatid(
    chat: Chat = Depends(get_chat_if_user_has_access_dependency),
):
    """
    Returns the chat with the given id

    Args:
        chat (Chat): The chat to be returned

    Returns:
        Chat: The chat with the given id
    """
    return chat


@chats_router.delete("/{chat_id}", status_code=204)
async def delete_chat_chatid(
    chat: Chat = Depends(get_chat_if_user_has_access_dependency),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """
    Deletes the chat with the given id

    Args:
        chat (Chat): The chat to be deleted

    Returns:
        None
    """
    crud_set_chat_membershipt_user_id_chat_id_inactive(
        db, chat_id=chat.id, member_id=current_user.id
    )


@chats_router.patch("/{chat_id}", response_model=Chat)
async def patch_chat_chatid(
    chat_updates: UpdateChat,
    chat: Chat = Depends(get_chat_if_user_has_access_dependency),
    db=Depends(get_db),
):
    """Updates chat's attributes like name, description, etc.

    Args:
        chat_updates (UpdateChat): The updates.
        chat (Chat): The chat to be updated.
        db (Session): Database session.

    Returns (Chat): Updated chat.
    """
    update_data = chat_updates.dict(exclude_unset=True)
    updated_chat = crud_update_chat(db, chat.id, update_data)

    if updated_chat is None:
        raise HTTPException(
            status_code=404,
            detail="The chat was not found.",
        )

    return updated_chat


@chats_router.delete("", status_code=204)
async def delete_chats(
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """
    Deletes all chats of the current user.

    Args:
        current_user (User): The current user
        db (Session): The database session

    Returns:
        None
    """
    crud_set_chat_membership_user_id_inactive(db, member_id=current_user.id)


@chats_router.post(
    "/{chat_id}/messages",
    response_model=Message,
    dependencies=[Depends(get_chat_if_user_has_access_dependency)],
)
async def post_chats_chatid_messages(
    message: CreateMessage = Depends(),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Creates a new message in the chat with the given id

    Args:
        message (CreateMessage): The message to be created

    """
    if message.artifact_version_id:
        artifact_version: ArtifactVersion = await get_artifact_version_dependency(
            message.artifact_version_id, db=db
        )
        artifact: Artifact = await get_artifact_from_artifact_version_dependency(
            artifact_version, db=db
        )
        await check_if_user_has_access_to_artifact(artifact, current_user)

    create_message = CreateMessageCRUD(**message.__dict__, sender_id=current_user.id)
    return crud_create_message(db, create_message)


@chats_router.get(
    "/{chat_id}/messages",
    response_model=MessagesResponse,
)
async def get_chats_chatid_messages(
    chat: Chat = Depends(get_chat_if_user_has_access_dependency),
    request_options: RequestOptions = Depends(),
    db=Depends(get_db),
):
    """
    Returns all messages from the given chat and applies filters, if any.

    Args:
        chat (Chat): The chat to be returned
        request_options (RequestOptions): The request options

    Returns:
        MessagesResponse: The messages from the given chat and metadata.
    """
    start_time = time.time()
    while True:
        result = crud_get_messages_by_chat_id_sorted_desc(
            db,
            chat_id=chat.id,
            limit=request_options.limit,
            offset=request_options.offset,
            from_date=request_options.from_date,
            to_date=request_options.to_date,
        )

        if (
            len(result) > 0
            or time.time() - start_time > CONFIG.LONG_POLLING_MAX_WAIT_TIME
            or not request_options.polling
        ):
            # Parse the messages.
            messages = [parse_chat_message(message) for message in result]

            # Compute the metadata.
            count = len(messages)
            total = crud_get_messages_total_number_by_chat_id_and_filters(
                db,
                chat_id=chat.id,
                from_date=request_options.from_date,
                to_date=request_options.to_date,
            )
            metadata = MessagesResponseMetadata(count=count, total=total)

            # Create the response.
            return MessagesResponse(metadata=metadata, data=messages)

        await asyncio.sleep(0.5)


@chats_router.get("/{chat_id}/messages/{message_id}", response_model=Message)
async def get_chats_chatid_messages_messageid(
    message: Message = Depends(get_message_if_user_has_access_dependency),
):
    """
    Returns the message with the given id of the chat with the given id

    Args:
        message (Message): The message to be returned

    Returns:
        Message: The message with the given id of the chat with the given id

    """
    return parse_chat_message(message)


@chats_router.post("/{chat_id}/messages/{message_id}/execute", status_code=204)
async def post_chats_chatid_messages_messageid(
    message: Message = Depends(get_message_if_user_has_access_dependency),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """
    Executes the message with the given id of the chat with the given id

    Args:
        message (Message): The message to be executed

    """
    artifact_config = {}
    if message.artifact_version_id:
        artifact_version: ArtifactVersion = await get_artifact_version_dependency(
            message.artifact_version_id, db=db
        )
        artifact: Artifact = await get_artifact_from_artifact_version_dependency(
            artifact_version, db=db
        )
        await check_if_user_has_access_to_artifact(artifact, current_user)
        await check_if_artifact_is_active(artifact)

        if not exists(os.path.join(artifact_version.artifact_uri, "config.json")):
            raise HTTPException(
                status_code=400,
                detail="The artifact version must contain a config.json file",
            )

        artifact_config = json.load(
            read_file(os.path.join(artifact_version.artifact_uri, "config.json"))
        )
        file_name = artifact_config.get("files", [dict()])[0].get("file_name", None)
        if not exists(os.path.join(artifact_version.artifact_uri, file_name)):
            raise HTTPException(
                status_code=400,
                detail=f"The artifact version must contain a file named {file_name}",
            )

        sas_url = get_signed_download_url(
            os.path.join(artifact_version.artifact_uri, file_name)
        )
        artifact_version_id = artifact_version.id
    else:
        sas_url = None
        artifact_version_id = None

    execution_app.send_task(
        "execute_user_message",
        args=(
            message.content,
            message.chat_id,
            message.id,
            artifact_version_id,
            sas_url,
            artifact_config,
        ),
    )

    return True
