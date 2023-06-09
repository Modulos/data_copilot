import os
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    ENVIRONMENT: str = Field(default="PROD", env="ENVIRONMENT")

    # Server
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    DB_CONNECTION_STRING: str = Field(..., env="DB_CONNECTION_STRING")
    STORAGE_BACKEND: str = Field(..., env="STORAGE_BACKEND")

    if "dfs.core.windows.net" in os.getenv("STORAGE_BACKEND", ""):
        AZURE_STORAGE_ACCOUNT_NAME: str = Field(..., env="AZURE_STORAGE_ACCOUNT_NAME")
        AZURE_STORAGE_ACCOUNT_KEY: str = Field(..., env="AZURE_STORAGE_ACCOUNT_KEY")
        CONTAINER_NAME: str = Field(..., env="CONTAINER_NAME")

    @property
    def POSTGRES_CONNECTION(self):
        return self.DB_CONNECTION_STRING
