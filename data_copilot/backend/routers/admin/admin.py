from fastapi import Depends, routing

from data_copilot.backend.dependencies.authentication import check_if_admin
from data_copilot.backend.routers.admin.groups import admin_groups_router
from data_copilot.backend.routers.admin.users import admin_users_router

admin_router = routing.APIRouter(
    prefix="/admin", dependencies=[Depends(check_if_admin)]
)
admin_router.include_router(admin_users_router)
admin_router.include_router(admin_groups_router)
