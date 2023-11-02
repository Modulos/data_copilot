from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Server
    DB_CONNECTION_STRING: str = Field(..., env="DB_CONNECTION_STRING")

    @property
    def POSTGRES_CONNECTION(self):
        return self.DB_CONNECTION_STRING
