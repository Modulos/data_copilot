import os
from datetime import timedelta
from unittest import TestCase

from fastapi.testclient import TestClient

from data_copilot.backend.crud.users import crud_get_user_by_email
from data_copilot.backend.database.psql import SessionLocal
from data_copilot.backend.main import app
from data_copilot.backend.schemas.authentication import User
from data_copilot.backend.utils.authentication import create_access_token

os.environ["ENVIRONMENT"] = "TEST"


def get_bearer_token(user):
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=10)
    )
    return access_token


class BasicTest(TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        db = SessionLocal()
        self.test_user = User(**crud_get_user_by_email(db, "test@modulos.ai").__dict__)
        self.admin_user = User(
            **crud_get_user_by_email(db, "admin@modulos.ai").__dict__
        )
        self.client = TestClient(app)
        self.bearer_token = get_bearer_token(self.test_user)
        self.admin_bearer_token = get_bearer_token(self.admin_user)
        self.auth_header = {"Authorization": f"Bearer {self.bearer_token}"}
        self.admin_auth_header = {"Authorization": f"Bearer {self.admin_bearer_token}"}
