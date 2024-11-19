import jwt

from datetime import datetime, timedelta
from passlib.context import CryptContext
from .db import get_user_from_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(hours=1),
    secret_key="secret_key",
    algorithm="HS256",
):

    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def authenticate_user(username: str, password: str):
    user = get_user_from_db(username)
    if not user or not verify_password(password, user["password"]):
        return None
    return user
