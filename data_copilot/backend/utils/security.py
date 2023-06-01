from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from data_copilot.backend.config import Config

CONFIG = Config()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
