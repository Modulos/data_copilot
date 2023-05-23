from fastapi import Depends, routing

from data_copilot.backend.crud.users import crud_create_user
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.authentication import get_current_active_user
from data_copilot.backend.dependencies.user_management import user_does_not_exist
from data_copilot.backend.schemas.authentication import CreateUser, GroupList, User

users_router = routing.APIRouter(prefix="/users")


@users_router.post("", response_model=User, dependencies=[Depends(user_does_not_exist)])
async def post_users(user: CreateUser, db=Depends(get_db)):
    return crud_create_user(db, user)


@users_router.get("/me", response_model=User)
async def get_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@users_router.get("/me/groups", response_model=GroupList)
async def get_users_me_groups(current_user: User = Depends(get_current_active_user)):
    return {"groups": [x.group.name for x in current_user.groups]}
