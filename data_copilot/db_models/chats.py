import uuid
from datetime import datetime
from typing import Optional, TypeVar

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from data_copilot.db_models.base import Base

User = TypeVar("User")
Artifact = TypeVar("Artifact")


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str]
    description: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id")
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    owner: Mapped["User"] = relationship(back_populates="chats_owner")
    members: Mapped[list["ChatMembership"]] = relationship(back_populates="chat")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")
    artifact: Mapped["Artifact"] = relationship(back_populates="chats")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chats.id")
    )
    sender_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    system_generated: Mapped[bool] = mapped_column(default=False)
    artifact_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifact_versions.id")
    )

    content: Mapped[str]
    content_type: Mapped[str] = mapped_column(default="text")

    sender: Mapped["User"] = relationship(back_populates="messages")
    chat: Mapped["Chat"] = relationship(back_populates="messages")


class ChatMembership(Base):
    __tablename__ = "chat_memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chats.id")
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    is_active: Mapped[bool] = mapped_column(default=True)

    chat: Mapped["Chat"] = relationship(back_populates="members")
    member: Mapped["User"] = relationship(back_populates="chats")
