import uuid
from typing import Optional, TypeVar

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_copilot.db_models.base import Base

Artifact = TypeVar("Artifact")
ChatMembership = TypeVar("ChatMembership")
Message = TypeVar("Message")
Chat = TypeVar("Chat")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    sso: Mapped[bool] = mapped_column(default=False)
    sso_provider: Mapped[Optional[str]]

    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    company: Mapped[Optional[str]]

    groups: Mapped[list["GroupMemberships"]] = relationship(back_populates="member")
    artifacts: Mapped[list["Artifact"]] = relationship(back_populates="user")
    chats: Mapped[list["ChatMembership"]] = relationship(back_populates="member")
    messages: Mapped[list["Message"]] = relationship(back_populates="sender")
    chats_owner: Mapped[list["Chat"]] = relationship(back_populates="owner")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(default="")
    is_admin: Mapped[bool] = mapped_column(default=False)

    members: Mapped[list["GroupMemberships"]] = relationship(back_populates="group")


class GroupMemberships(Base):
    __tablename__ = "group_memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id")
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    group: Mapped["Group"] = relationship(back_populates="members")
    member: Mapped["User"] = relationship(back_populates="groups")
