from fastapi import routing
from data_copilot.backend.config import Config

CONFIG = Config()

health_router = routing.APIRouter(prefix="/health")


@health_router.get("", response_model=str)
async def health_check():
    return "OK"
