import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ENVIRONMENT: str = Field(default="PROD", validation_alias="ENVIRONMENT")

    # Server
    CELERY_BROKER_URL: str = Field(..., validation_alias="CELERY_BROKER_URL")
    DB_CONNECTION_STRING: str = Field(..., validation_alias="DB_CONNECTION_STRING")
    STORAGE_BACKEND: str = Field(..., validation_alias="STORAGE_BACKEND")

    if "dfs.core.windows.net" in os.getenv("STORAGE_BACKEND", ""):
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
