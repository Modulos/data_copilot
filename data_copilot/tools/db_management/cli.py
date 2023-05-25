import logging
from typing import Dict

import click
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data_copilot.db_models import artifacts as artifact_model
from data_copilot.db_models import users as user_model
from data_copilot.db_models.base import Base
from tools.db_management.psql import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def crud_create_user(db: Session, user: Dict):
    hashed_password = pwd_context.hash(user.get("password"))
    user.pop("password")
    db_user = user_model.User(**user, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@click.group()
def cli():
    pass


@cli.group()
def schema():
    """
    Schema management commands
    """
    pass


@schema.command()
def show():
    """
    Show the database schema
    """
    for table in Base.metadata.sorted_tables:
        print(table.name)
        for column in table.columns:
            print(f"  {column.name} {column.type}")
        print("\n")


@schema.command()
def update():
    """
    Update the database schema and create all tables
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Schema updated")


@schema.command()
def drop():
    """
    Drop all tables in the database
    """
    click.confirm("Are you sure you want to reset the database?", abort=True)
    logging.info("Resetting database")
    db = SessionLocal()
    db.execute("DROP SCHEMA public CASCADE")
    db.execute("CREATE SCHEMA public")
    db.commit()
    logging.info("Database reset complete")
    Base.metadata.drop_all(bind=engine)
    logger.info("Schema dropped")


@cli.group()
def data():
    """
    Data management commands
    """
    pass


@data.group()
def users():
    pass


@users.command()
@click.argument("email")
@click.argument("password")
def create(email, password):  # noqa E811
    """
    Create a new user
    """
    db = SessionLocal()
    try:
        user = crud_create_user(db, {"email": email, "password": password})
        logger.info(f"User {user.email} created")
    except IntegrityError:
        logger.error(f"User {email} already exists")


@users.command()
@click.argument("email")
def delete(email):
    """
    Delete a user
    """
    db = SessionLocal()
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if user:
        # remove all group memberships
        click.confirm(f"Are you sure you want to delete {email}?", abort=True)
        db.query(user_model.GroupMemberships).filter(
            user_model.GroupMemberships.member_id == user.id
        ).delete()
        db.delete(user)
        db.commit()
        logger.info(f"User {email} deleted")
    else:
        logger.error(f"User {email} not found")


@data.group()
def groups():
    """
    Group management commands
    """
    pass


@groups.command()
@click.argument("name")
@click.option("--admin", is_flag=True)
@click.option("--description")
def create(name, admin, description):  # noqa E811
    """
    Create a new group
    """
    db = SessionLocal()
    try:
        group = user_model.Group(name=name, is_admin=admin, description=description)
        db.add(group)
        db.commit()
        db.refresh(group)
        logger.info(f"Group {group.name} created")
    except IntegrityError:
        logger.error(f"Group {name} already exists")


@groups.command()
@click.argument("name")
def delete(name):  # noqa E811
    """
    Delete a group
    """
    db = SessionLocal()
    group = db.query(user_model.Group).filter(user_model.Group.name == name).first()
    if group:
        click.confirm(f"Are you sure you want to delete {name}?", abort=True)
        # remove all group memberships
        db.query(user_model.GroupMemberships).filter(
            user_model.GroupMemberships.group_id == group.id
        ).delete()
        db.delete(group)
        db.commit()
        logger.info(f"Group {name} deleted")
    else:
        logger.error(f"Group {name} not found")


@groups.command()
@click.argument("name")
@click.argument("email")
def add_user(name, email):
    """
    Add a user to a group
    """
    db = SessionLocal()
    group = db.query(user_model.Group).filter(user_model.Group.name == name).first()
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if group and user:
        membership = user_model.GroupMemberships(group_id=group.id, member_id=user.id)
        db.add(membership)
        db.commit()
        logger.info(f"User {email} added to group {name}")
    else:
        logger.error(f"Group {name} or user {email} not found")


@groups.command()
@click.argument("name")
@click.argument("email")
def remove_user(name, email):
    """
    Remove a user from a group
    """
    db = SessionLocal()
    group = db.query(user_model.Group).filter(user_model.Group.name == name).first()
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if group and user:
        membership = (
            db.query(user_model.GroupMemberships)
            .filter(user_model.GroupMemberships.group_id == group.id)
            .filter(user_model.GroupMemberships.member_id == user.id)
            .first()
        )
        if membership:
            db.delete(membership)
            db.commit()
            logger.info(f"User {email} removed from group {name}")
        else:
            logger.error(f"User {email} is not a member of group {name}")
    else:
        logger.error(f"Group {name} or user {email} not found")


@data.group()
def artifact_types():
    """
    Artifact type management commands
    """
    pass


@artifact_types.command()
@click.argument("name")
@click.option("--description")
def create(name, description):  # noqa E811
    """
    Create a new artifact type
    """
    db = SessionLocal()
    try:
        artifact_type = artifact_model.ArtifactType(name=name, description=description)
        db.add(artifact_type)
        db.commit()
        db.refresh(artifact_type)
        logger.info(f"Artifact type {artifact_type.name} created")
    except IntegrityError:
        logger.error(f"Artifact type {name} already exists")


@artifact_types.command()
@click.argument("name")
def delete(name):  # noqa E811
    """
    Delete an artifact type
    """
    db = SessionLocal()
    artifact_type = (
        db.query(artifact_model.ArtifactType)
        .filter(artifact_model.ArtifactType.name == name)
        .first()
    )
    if artifact_type:
        click.confirm(f"Are you sure you want to delete {name}?", abort=True)
        db.delete(artifact_type)
        db.commit()
        logger.info(f"Artifact type {name} deleted")
    else:
        logger.error(f"Artifact type {name} not found")


if __name__ == "__main__":
    cli()
