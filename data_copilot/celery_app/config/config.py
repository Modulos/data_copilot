from pydantic import BaseSettings, Field


class Config(BaseSettings):
    ENVIRONMENT: str = Field(default="PROD", env="ENVIRONMENT")

    # Server
    REDIS_URL: str = Field(..., env="REDIS_URL")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(..., env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")

    @property
    def POSTGRES_CONNECTION(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
