import logging

from alembic import command, config
from sqlalchemy import text

from data_copilot.backend.database.psql import SessionLocal, engine

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    db = SessionLocal()

    # reset database
    db.execute(text("DROP SCHEMA public CASCADE"))
    db.execute(text("CREATE SCHEMA public"))
    db.commit()

    # This uses the alembic.ini config file, but the sqlalchemy.url entry
    # gets overwritten inside db_migrations/env.py.
    alembic_cfg = config.Config("alembic.ini")

    # Link multiple commands into a single connection and transaction.
    # This might not be necessary in this case because we only call the
    # `upgrade` command once, but the approach will be useful in the future
    # when we will try to run more complex command sequences.
    #
    # For more details please consult the official documentation:
    # https://alembic.sqlalchemy.org/en/latest/api/commands.html
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
