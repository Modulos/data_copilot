from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from data_copilot.backend.config import Config
from data_copilot.backend.crud.users import crud_get_user_by_email
from data_copilot.backend.database.psql import get_db
from data_copilot.backend.schemas.authentication import TokenData, User
from data_copilot.backend.utils.security import oauth2_scheme

CONFIG = Config()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db=Depends(get_db)
) -> User:
    """Returns the user if the credentials are valid.

    Args:
        token (str): The token.
        db (Session): Database session.

    Raises:
        HTTPException: If the credentials are not valid or missing.

    Returns (User): The user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud_get_user_by_email(db, token_data.username)
    if user is None:
        raise credentials_exception
    return User.from_orm(user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Returns the user if it is active.

    Args:
        current_user (User): The user.

    Raises:
        HTTPException: If the user is inactive.

    Returns (User): The user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return User.from_orm(current_user)


async def check_if_admin(current_user: User = Depends(get_current_active_user)) -> bool:
    """Checks if the user is admin.

    Args:
        current_user (User): The user.

    Raises:
        HTTPException: If the user is not admin.

    Returns (bool): True if it is admin.
    """
    is_admin = max([x.group.is_admin for x in current_user.groups] + [False])
    if not is_admin:
        raise HTTPException(status_code=400, detail="Not an admin")
    return True
