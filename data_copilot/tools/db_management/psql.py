from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tools.db_management.config import Config

CONFIG = Config()

SQLALCHEMY_DATABASE_URL = CONFIG.POSTGRES_CONNECTION
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "sslmode": "allow",
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
