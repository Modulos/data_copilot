from sqlalchemy.orm import DeclarativeBase
from data_copilot.db_models.helpers import compile_uuid_sqlite  # noqa


class Base(DeclarativeBase):
    pass
