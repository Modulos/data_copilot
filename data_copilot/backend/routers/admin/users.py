from fastapi import Depends, routing

from data_copilot.backend.crud.users import (
    crud_add_user_to_group,
    crud_create_user,
    crud_delete_user,
    crud_get_users,
    crud_remove_user_from_group,
)
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.user_management import (
    get_group_by_name,
    get_user_by_email,
    get_user_by_user_id,
    user_does_not_exist,
    user_not_in_group,
)
from data_copilot.backend.schemas.authentication import CreateUser, Group, User

admin_users_router = routing.APIRouter(prefix="/users")


@admin_users_router.get("", response_model=list[User])
async def get_users(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    return crud_get_users(db, skip, limit)


@admin_users_router.post(
    "", response_model=User, dependencies=[Depends(user_does_not_exist)]
)
async def post_users(user: CreateUser, db=Depends(get_db)):
    return crud_create_user(db, user)


@admin_users_router.get("/{user_id}", response_model=User)
async def get_users_userid(user: User = Depends(get_user_by_user_id)):
    return user


@admin_users_router.get("/query/{email}", response_model=User)
async def get_users_query_email(user: User = Depends(get_user_by_email)):
    return user


@admin_users_router.delete("/{user_id}", status_code=204)
async def delete_users(user: User = Depends(get_user_by_user_id), db=Depends(get_db)):
    crud_delete_user(db, user.id)
    return None


@admin_users_router.post(
    "/{user_id}/group", status_code=201, dependencies=[Depends(user_not_in_group)]
)
async def post_users_group(
    user: User = Depends(get_user_by_user_id),
    group: Group = Depends(get_group_by_name),
    db=Depends(get_db),
):
    """
    Adds a user to a group.
    """
    crud_add_user_to_group(db, user, group)


@admin_users_router.delete("/{user_id}/group", status_code=204)
async def delete_users_group(
    user: User = Depends(get_user_by_user_id),
    group: Group = Depends(get_group_by_name),
    db=Depends(get_db),
):
    crud_remove_user_from_group(db, user.id, group.id)
