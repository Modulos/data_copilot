import uuid

from fastapi import Depends, HTTPException

from data_copilot.backend.crud.users import (
    crud_get_group_by_name,
    crud_get_user,
    crud_get_user_by_email,
)
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.schemas.authentication import (
    CreateGroup,
    CreateUser,
    Group,
    User,
)


async def get_user_by_email(email: str, db=Depends(get_db)) -> User:
    """Returns user based on the email.

    Args:
        email (str): User's email.
        db (Session): Database session.

    Raises:
        HTTPException: If the user was not found.

    Returns (User): The user.
    """
    user = crud_get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_orm(user)


async def get_user_by_user_id(user_id: uuid.UUID, db=Depends(get_db)) -> User:
    """Returns user based on the user ID.

    Args:
        user_id (UUID): User's ID.
        db (Session): Database session.

    Raises:
        HTTPException: If the user was not found.

    Returns (User): The user.
    """
    user = crud_get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_orm(user)


async def get_group_by_name(group_name: str, db=Depends(get_db)) -> Group:
    """Returns user group based on the group name.

    Args:
        group_name (str): Group's name.
        db (Session): Database session.

    Raises:
        HTTPException: If the group was not found.

    Returns (Group): The group.
    """
    group = crud_get_group_by_name(db, group_name)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return Group.from_orm(group)


async def user_does_not_exist(user: CreateUser, db=Depends(get_db)) -> None:
    """Checks if the user does not exist.

    Args:
        user (CreateUser): The user.
        db (Session): Database session.

    Raises:
        HTTPException: If the user already exists.
    """
    user = crud_get_user_by_email(db, user.email)
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")


async def group_does_not_exist(group: CreateGroup, db=Depends(get_db)) -> None:
    """Checks if the group does not exist.

    Args:
        group (CreateGroup): The group.
        db (Session): Database session.

    Raises:
        HTTPException: If the group already exists.
    """
    group = crud_get_group_by_name(db, group.name)
    if group is not None:
        raise HTTPException(status_code=400, detail="Group already exists")


async def user_is_in_group(
    user: User = Depends(get_user_by_email), group: Group = Depends(get_group_by_name)
) -> None:
    """Checks if the user is in the group.

    Args:
        user (User): The user.
        group (Group): The group.

    Raises:
        HTTPException: If the user is not in the group.
    """
    if group.name not in [x.group.name for x in user.groups]:
        raise HTTPException(
            status_code=400, detail=f"User {user.email} not in group {group.name}"
        )


async def user_not_in_group(
    user: User = Depends(get_user_by_email), group: Group = Depends(get_group_by_name)
) -> None:
    """Checks if the user is not in the group.

    Args:
        user (User): The user.
        group (Group): The group.

    Raises:
        HTTPException: If the user is already in the group.
    """
    if group.name in [x.group.name for x in user.groups]:
        raise HTTPException(
            status_code=400, detail=f"User {user.email} already in group {group.name}"
        )
