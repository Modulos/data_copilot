import os
from typing import Dict

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    # Server
    BACKEND_HOST: str = Field(..., env="BACKEND_HOST")
    # ENVIRONMENT from env variable default to "PROD"
    ENVIRONMENT: str = Field(default="PROD", env="ENVIRONMENT")

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LONG_POLLING_MAX_WAIT_TIME: int = 20

    ALLOWED_ARTIFACTS_CONTENT_TYPES: Dict[str, str] = {
        "text/csv": "csv",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    }

    if os.getenv("ENVIRONMENT") != "TEST":
        DB_CONNECTION_STRING: str = Field(..., env="DB_CONNECTION_STRING")
        SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
        AZURE_STORAGE_ACCOUNT_NAME: str = Field(..., env="AZURE_STORAGE_ACCOUNT_NAME")
        AZURE_STORAGE_ACCOUNT_KEY: str = Field(..., env="AZURE_STORAGE_ACCOUNT_KEY")
        CONTAINER_NAME: str = Field(..., env="CONTAINER_NAME")
        STORAGE_BACKEND: str = Field(..., env="STORAGE_BACKEND")
        BACKEND_HOST: str = Field(..., env="BACKEND_HOST")

        CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")

    elif os.getenv("ENVIRONMENT") == "TEST":
        secret_key = "c86d3444a380bb36cca7abe1b6dcc8caaee0ecf5bbe254c5473783d147ebc12e"
        SECRET_KEY: str = secret_key
        BACKEND_HOST: str = "http://localhost:8000/api"
        STORAGE_BACKEND: str = "./artifacts/"
        CELERY_BROKER_URL: str = ""

    @property
    def POSTGRES_CONNECTION(self):
        return self.DB_CONNECTION_STRING
