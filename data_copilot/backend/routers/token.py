from datetime import timedelta

from fastapi import Depends, HTTPException, routing, status
from fastapi.security import OAuth2PasswordRequestForm

from data_copilot.backend.config import Config
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.dependencies.authentication import get_current_active_user
from data_copilot.backend.schemas.authentication import Token, User
from data_copilot.backend.utils.authentication import (
    authenticate_user,
    create_access_token,
)

CONFIG = Config()
token_router = routing.APIRouter(prefix="/token")


@token_router.post("", response_model=Token, include_in_schema=False)
@token_router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the
                                               username and password

    Returns:
        Token: The access token
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@token_router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """
    Refresh the access token. This is used to refresh the access token before
    it expires.

    Args:
        current_user (User): The current user

    Returns:
        Token: The access token

    """
    access_token_expires = timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
