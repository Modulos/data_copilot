import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_copilot.celery_app.config import Config

CONFIG = Config()

if os.getenv("ENVIRONMENT") == "TEST":
    from sqlalchemy import create_mock_engine

    def dump(sql, *multiparams, **params):
        print(sql.compile(dialect=engine.dialect))

    engine = create_mock_engine("postgresql+psycopg2://", dump)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

else:
    SQLALCHEMY_DATABASE_URL = CONFIG.POSTGRES_CONNECTION

    if "postgresql://" in SQLALCHEMY_DATABASE_URL:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"sslmode": "allow"}
        )
    elif "sqlite://" in SQLALCHEMY_DATABASE_URL:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            pool_size=5,
            max_overflow=10,
        )
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
