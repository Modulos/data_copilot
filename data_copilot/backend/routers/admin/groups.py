from fastapi import Depends, routing

from data_copilot.backend.crud.users import (
    crud_create_group,
    crud_delete_group,
    crud_get_groups,
)
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.user_management import (
    get_group_by_name,
    group_does_not_exist,
)
from data_copilot.backend.schemas.authentication import CreateGroup, Group

admin_groups_router = routing.APIRouter(prefix="/groups")


@admin_groups_router.get("", response_model=list[Group])
async def get_groups(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """
    Returns all the groups.

    Args:
        skip (int, optional): The number of groups to skip. Defaults to 0.
        limit (int, optional): The number of groups to return. Defaults to 100.

    Returns:
        list[Group]: A list of groups
    """
    return crud_get_groups(db, skip, limit)


@admin_groups_router.post("", dependencies=[Depends(group_does_not_exist)])
async def post_groups(group: CreateGroup, db=Depends(get_db)):
    """
    Create a new group with name and description. Returns
    the created group.

    Args:
        group (CreateGroup): The group to create

    Returns:
        Group: The created group
    """
    return crud_create_group(db, group)


@admin_groups_router.delete("", status_code=204)
async def delete_groups(group: Group = Depends(get_group_by_name), db=Depends(get_db)):
    """
    Delete a group. Returns None.
    """
    crud_delete_group(db, group.id)
    return None
