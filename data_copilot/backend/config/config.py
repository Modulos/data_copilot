import os
from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Server
    BACKEND_HOST: str = Field(..., validation_alias="BACKEND_HOST")
    # ENVIRONMENT from env variable default to "PROD"
    ENVIRONMENT: str = Field(default="PROD", validation_alias="ENVIRONMENT")

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LONG_POLLING_MAX_WAIT_TIME: int = 20

    ALLOWED_ARTIFACTS_CONTENT_TYPES: Dict[str, str] = {
        "text/csv": "csv",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    }
    COMPUTE_BACKEND: str = Field(..., validation_alias="COMPUTE_BACKEND")

    if os.getenv("ENVIRONMENT") != "TEST":
        DB_CONNECTION_STRING: str = Field(..., validation_alias="DB_CONNECTION_STRING")
        SECRET_KEY: str = Field(..., validation_alias="JWT_SECRET_KEY")
        STORAGE_BACKEND: str = Field(..., validation_alias="STORAGE_BACKEND")
        BACKEND_HOST: str = Field(..., validation_alias="BACKEND_HOST")

        CELERY_BROKER_URL: str = Field(..., validation_alias="CELERY_BROKER_URL")

    elif os.getenv("ENVIRONMENT") == "TEST":
        secret_key = "c86d3444a380bb36cca7abe1b6dcc8caaee0ecf5bbe254c5473783d147ebc12e"
        SECRET_KEY: str = secret_key
        BACKEND_HOST: str = "http://localhost:8000/api"
        STORAGE_BACKEND: str = "file://./artifacts/"
        CELERY_BROKER_URL: str = ""

    if "dfs.core.windows.net" in os.getenv("STORAGE_BACKEND"):
        AZURE_STORAGE_ACCOUNT_NAME: str = Field(
            ..., validation_alias="AZURE_STORAGE_ACCOUNT_NAME"
        )
        AZURE_STORAGE_ACCOUNT_KEY: str = Field(
            ..., validation_alias="AZURE_STORAGE_ACCOUNT_KEY"
        )
        CONTAINER_NAME: str = Field(..., validation_alias="CONTAINER_NAME")

    @property
    def POSTGRES_CONNECTION(self):
        return self.DB_CONNECTION_STRING
