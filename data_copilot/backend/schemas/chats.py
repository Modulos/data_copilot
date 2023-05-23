import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, parse_obj_as, validator


class CreateChat(BaseModel):
    name: str
    description: str = ""
    artifact_id: uuid.UUID | None = None


class CreateChatCRUD(CreateChat):
    owner_id: uuid.UUID


class Chat(CreateChatCRUD):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True


class UpdateChat(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @validator("name")
    def name_must_be_not_none(cls, v):
        if v is None:
            raise ValueError("must be not None")

        return v

    @validator("description")
    def description_must_be_not_none(cls, v):
        if v is None:
            raise ValueError("must be not None")

        return v


class CreateMessage(BaseModel):
    content: str
    chat_id: uuid.UUID
    artifact_version_id: uuid.UUID | None = None


class ContentTypes(str, Enum):
    text = "text"
    json = "json"
    error = "error"


class CreateMessageCRUD(CreateMessage):
    sender_id: uuid.UUID | None = None
    system_generated: bool = False
    content_type: ContentTypes = ContentTypes.text


class CreateChatMembershipCRUD(BaseModel):
    chat_id: uuid.UUID
    member_id: uuid.UUID


class ChatMembership(CreateChatMembershipCRUD):
    id: uuid.UUID
    is_active: bool = True

    class Config:
        orm_mode = True


class RequestOptions(BaseModel):
    limit: int = Field(20, ge=1, le=100, type=int)
    offset: int = Field(0, ge=0, type=int)

    from_date: datetime | None = None
    to_date: datetime | None = None

    polling: bool = False


class MessageComponentsConfigs(BaseModel):
    show_title: bool | None = None
    show_description: bool | None = None
    highlight_columns: list[str] | None = None
    highlight_values_from_table: bool | None = None


class ComponentTypes(str, Enum):
    table = "table"
    text = "text"
    plot_hist = "plot_hist"
    plot_bar = "plot_bar"
    plot_heatmap = "plot_heatmap"


class MessageComponents(BaseModel):
    type: ComponentTypes
    name: str | None = None
    description: str | None = None
    config: MessageComponentsConfigs | None = None
    data: dict | None = None


class MessageJsonContent(BaseModel):
    method_name: str
    components: list[MessageComponents]


class Message(CreateMessageCRUD):
    id: uuid.UUID
    created_at: datetime
    content: MessageJsonContent | str | None = None

    class Config:
        orm_mode = True


class MessagesResponseMetadata(BaseModel):
    count: int
    total: int


class MessagesResponse(BaseModel):
    metadata: MessagesResponseMetadata
    data: list[Message]


def parse_chat_message(message: Message) -> Message:
    if message.content_type == "json":
        try:
            content_json = json.loads(message.content)
        except json.JSONDecodeError as e:
            logging.error(f"Could not parse message content: {message.content}")
            raise e
        message.content = parse_obj_as(MessageJsonContent, content_json)
    return message
