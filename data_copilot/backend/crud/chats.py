import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from data_copilot.backend.schemas import chats as chats_schema
from data_copilot.db_models import chats as chats_model


def crud_create_chat(db: Session, chat: chats_schema.CreateChatCRUD):
    db_chat = chats_model.Chat(**chat.__dict__)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def crud_get_chat(db: Session, chat_id: uuid.UUID):
    return db.scalars(
        select(chats_model.Chat).filter(chats_model.Chat.id == chat_id).limit(1)
    ).first()


def crud_get_all_chats_with_user_id(db: Session, user_id: uuid.UUID):
    return db.scalars(
        select(chats_model.Chat)
        .join(chats_model.ChatMembership)
        .filter(chats_model.ChatMembership.member_id == user_id)
        .filter(chats_model.ChatMembership.is_active)
        .order_by(chats_model.Chat.created_at.desc())
    ).all()


def crud_update_chat(
    db: Session, chat_id: uuid.UUID, update_data: dict
) -> Optional[chats_model.Chat]:
    """Updates chat's attributes like name, description, etc.

    Args:
        db (Session): Database session.
        chat_id (UUID): Chat ID.
        update_data (dict): The updates.

    Returns (Chat): Updated chat.
    """
    db_chat = db.get(chats_model.Chat, chat_id)

    if db_chat is None:
        return None

    for key, value in update_data.items():
        setattr(db_chat, key, value)

    db.commit()

    return db_chat


def crud_get_chat_with_user_id(db: Session, chat_id: uuid.UUID, user_id: uuid.UUID):
    return db.scalars(
        select(chats_model.Chat)
        .join(chats_model.ChatMembership)
        .filter(chats_model.ChatMembership.chat_id == chat_id)
        .filter(chats_model.ChatMembership.member_id == user_id)
        .filter(chats_model.ChatMembership.is_active)
        .limit(1)
    ).first()


def crud_create_chat_membership(
    db: Session, chat_membership: chats_schema.CreateChatMembershipCRUD
):
    db_chat_membership = chats_model.ChatMembership(**chat_membership.__dict__)
    db.add(db_chat_membership)
    db.commit()
    db.refresh(db_chat_membership)
    return db_chat_membership


def crud_set_chat_membershipt_user_id_chat_id_inactive(
    db: Session, chat_id: uuid.UUID, member_id: uuid.UUID
):
    db_chat_membership = db.scalars(
        select(chats_model.ChatMembership)
        .filter(chats_model.ChatMembership.chat_id == chat_id)
        .filter(chats_model.ChatMembership.member_id == member_id)
        .filter(chats_model.ChatMembership.is_active)
    ).all()
    for chat_membership in db_chat_membership:
        chat_membership.is_active = False
    db.commit()
    return True


def crud_set_chat_membership_user_id_inactive(db: Session, member_id: uuid.UUID):
    db_chat_membership = db.scalars(
        select(chats_model.ChatMembership)
        .filter(chats_model.ChatMembership.member_id == member_id)
        .filter(chats_model.ChatMembership.is_active)
    ).all()
    for chat_membership in db_chat_membership:
        chat_membership.is_active = False
    db.commit()
    return True


def crud_create_message(db: Session, message: chats_schema.CreateMessageCRUD):
    db_message = chats_model.Message(**message.__dict__)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def crud_get_messages_by_chat_id_sorted_desc(
    db: Session,
    chat_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    if from_date and to_date:
        return db.scalars(
            select(chats_model.Message)
            .filter(chats_model.Message.chat_id == chat_id)
            .filter(chats_model.Message.created_at > from_date)
            .filter(chats_model.Message.created_at <= to_date)
            .order_by(chats_model.Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    if from_date:
        return db.scalars(
            select(chats_model.Message)
            .filter(chats_model.Message.chat_id == chat_id)
            .filter(chats_model.Message.created_at > from_date)
            .order_by(chats_model.Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    if to_date:
        return db.scalars(
            select(chats_model.Message)
            .filter(chats_model.Message.chat_id == chat_id)
            .filter(chats_model.Message.created_at <= to_date)
            .order_by(chats_model.Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    return db.scalars(
        select(chats_model.Message)
        .filter(chats_model.Message.chat_id == chat_id)
        .order_by(chats_model.Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()


def crud_get_messages_total_number_by_chat_id_and_filters(
    db: Session,
    chat_id: uuid.UUID,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> int:
    """Returns the number of messages in a given chat based on the filters.

    Args:
        db (Session): Database session.
        chat_id (uuid.UUID): Chat's ID.
        from_date (datetime): Start date.
        to_date (datetime): End date.

    Returns (int): The number of messages.
    """

    if from_date and to_date:
        return (
            db.query(func.count(chats_model.Message.id))
            .filter(chats_model.Message.chat_id == chat_id)
            .filter(chats_model.Message.created_at > from_date)
            .filter(chats_model.Message.created_at <= to_date)
            .scalar()
        )

    if from_date:
        return (
            db.query(func.count(chats_model.Message.id))
            .filter(chats_model.Message.chat_id == chat_id)
            .filter(chats_model.Message.created_at > from_date)
            .scalar()
        )

    if to_date:
        return (
            db.query(func.count(chats_model.Message.id))
            .filter(chats_model.Message.chat_id == chat_id)
            .filter(chats_model.Message.created_at <= to_date)
            .scalar()
        )

    return (
        db.query(func.count(chats_model.Message.id))
        .filter(chats_model.Message.chat_id == chat_id)
        .scalar()
    )


def crud_get_message_by_chat_id_and_message_id(
    db: Session, chat_id: uuid.UUID, message_id: uuid.UUID
):
    return db.scalars(
        select(chats_model.Message)
        .filter(chats_model.Message.chat_id == chat_id)
        .filter(chats_model.Message.id == message_id)
        .limit(1)
    ).first()
