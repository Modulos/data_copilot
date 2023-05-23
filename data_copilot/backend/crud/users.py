import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from data_copilot.backend.schemas import authentication as user_schema
from data_copilot.backend.utils.security import pwd_context
from data_copilot.db_models import users as user_model


def crud_get_user(db: Session, user_id: uuid.UUID):
    return db.scalars(
        select(user_model.User).filter(user_model.User.id == user_id).limit(1)
    ).first()


def crud_get_group(db: Session, group_id: uuid.UUID):
    return db.scalars(
        select(user_model.Group).filter(user_model.Group.id == group_id).limit(1)
    ).first()


def crud_get_user_by_email(db: Session, email: str) -> user_schema.User:
    return db.scalars(
        select(user_model.User).filter(user_model.User.email == email).limit(1)
    ).first()


def crud_get_sso_user_by_email(db: Session, email: str, provider: str):
    return db.scalars(
        select(user_model.User)
        .filter(user_model.User.email == email)
        .filter(user_model.User.sso_provider == provider)
        .filter(user_model.User.sso)
        .limit(1)
    ).first()


def crud_get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(user_model.User).offset(skip).limit(limit)).all()


def crud_get_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(user_model.Group).offset(skip).limit(limit)).all()


def crud_create_user(db: Session, user: user_schema.CreateUser):
    hashed_password = pwd_context.hash(user.password)
    user_dict = user.dict()
    user_dict.pop("password")
    db_user = user_model.User(**user_dict, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def crud_create_sso_user(db: Session, user: user_schema.CreateUser, provider: str):
    user_dict = user.dict()
    user_dict.pop("password")
    db_user = user_model.User(**user_dict, sso=True, sso_provider=provider)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def crud_add_user_to_group(
    db: Session, user: user_schema.User, group: user_schema.Group
):
    group_membership = user_schema.CreateGroupMembership(
        group_id=group.id, member_id=user.id
    )
    db_group_membership = user_model.GroupMemberships(**group_membership.dict())
    db.add(db_group_membership)
    db.commit()
    return crud_get_user(db, user.id)


def crud_remove_user_from_group(db: Session, user_id: uuid.UUID, group_id: uuid.UUID):
    db.execute(
        delete(user_model.GroupMemberships)
        .where(user_model.GroupMemberships.group_id == group_id)
        .where(user_model.GroupMemberships.member_id == user_id)
    )
    db.commit()


def crud_create_group(db: Session, group: user_schema.CreateGroup):
    db_group = user_model.Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def crud_get_group_by_name(db: Session, name: str):
    return db.scalars(
        select(user_model.Group).filter(user_model.Group.name == name).limit(1)
    ).first()


def crud_delete_user(db: Session, user_id: uuid.UUID):
    db.execute(
        delete(user_model.GroupMemberships).where(
            user_model.GroupMemberships.member_id == user_id
        )
    )
    db.execute(delete(user_model.User).where(user_model.User.id == user_id))
    db.commit()


def crud_delete_group(db: Session, group_id: uuid.UUID):
    db.execute(
        delete(user_model.GroupMemberships).where(
            user_model.GroupMemberships.group_id == group_id
        )
    )
    db.execute(delete(user_model.Group).where(user_model.Group.id == group_id))
    db.commit()
