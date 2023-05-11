import logging

from alembic import command, config
from sqlalchemy import text

from backend.crud.users import (
    crud_add_user_to_group,
    crud_create_group,
    crud_create_user,
    crud_get_group_by_name,
    crud_get_user_by_email,
)
from backend.database.psql import SessionLocal, engine
from backend.schemas import authentication as authentication_schema

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

    test_user = crud_get_user_by_email(db, email="test@modulos.ai")

    if not test_user:
        logger.info("Creating test user")
        test_user = crud_create_user(
            db,
            authentication_schema.CreateUser(
                email="test@modulos.ai",
                password="test",
            ),
        )
    else:
        logger.info("Test user already exists")

    # Check if admin user "admin@example.com" exists
    admin_user = crud_get_user_by_email(db, email="admin@modulos.ai")

    # If admin user does not exist, create it
    if not admin_user:
        logger.info("Creating admin user")
        admin_user = crud_create_user(
            db,
            authentication_schema.CreateUser(
                email="admin@modulos.ai",
                password="EmpiFPkclLujLxNLe5eEnCr7XbJaHlEiL9XDns9ebI4",
            ),
        )
    else:
        logger.info("Admin user already exists")

    # check if admin group "admin" exists
    admin_group = crud_get_group_by_name(db, name="admin")

    # If admin group does not exist, create it
    if not admin_group:
        logger.info("Creating admin group")
        admin_group = crud_create_group(
            db, authentication_schema.CreateGroup(name="admin", is_admin=True)
        )
    else:
        logger.info("Admin group already exists")

    # Make sure that the admin user is in the admin group.
    if admin_group not in admin_user.groups:
        admin_user = crud_add_user_to_group(db, user=admin_user, group=admin_group)
