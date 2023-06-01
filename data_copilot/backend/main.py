from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_copilot.backend.config import Config
from data_copilot.backend.database.psql import engine
from data_copilot.backend.routers.admin.admin import admin_router as admin_router
from data_copilot.backend.routers.artifacts import artifacts_router
from data_copilot.backend.routers.chats import chats_router
from data_copilot.backend.routers.health import health_router
from data_copilot.backend.routers.token import token_router
from data_copilot.backend.routers.users import users_router as users_router
from data_copilot.db_models import *  # noqa F401 F403
from data_copilot.db_models.base import Base

CONFIG = Config()

Base.metadata.create_all(bind=engine)

if CONFIG.ENVIRONMENT in ["TEST", "DEVELOPMENT"]:
    app = FastAPI(
        title="API_NAME",
        description="API_DESC",
        version="0.2.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        swagger_ui_oauth2_redirect_url="/api/docs/oauth2-redirect",
    )
else:
    app = FastAPI(
        title="API_NAME",
        description="API_DESC",
        version="0.2.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        swagger_ui_oauth2_redirect_url=None,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8010",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:80",
        "http://127.0.0.1",
        "http://localhost:8080",
        "http://localhost:8010",
        "http://localhost:8000",
        "http://localhost:80",
        "http://localhost",
        "http://172.20.0.10:80",
        "https://data-copilot.azurefd.net/",
    ],
    allow_origin_regex=r"https://.*\.data-copilot\.ai",
    allow_credentials=True,
    allow_methods=["POST", "GET", "PATCH", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

router = APIRouter(prefix="/api")
router.include_router(health_router, tags=["users"])
router.include_router(users_router, tags=["users"])
router.include_router(admin_router, tags=["admin"])
router.include_router(token_router, tags=["authenication"])
router.include_router(artifacts_router, tags=["artifact"])
router.include_router(chats_router, tags=["chat"])


app.include_router(router)
