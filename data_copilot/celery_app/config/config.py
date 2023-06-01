from pydantic import BaseSettings, Field


class Config(BaseSettings):
    ENVIRONMENT: str = Field(default="PROD", env="ENVIRONMENT")

    # Server
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    DB_CONNECTION_STRING: str = Field(..., env="DB_CONNECTION_STRING")

    @property
    def POSTGRES_CONNECTION(self):
        return self.DB_CONNECTION_STRING
