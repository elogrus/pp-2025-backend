from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from database.context import repository
from database.models import User
from database.repository.repository import Repository

# Конфигурация
SECRET_KEY = "ваш_секретный_ключ"  # На практике используйте .env
REFRESH_SECRET_KEY = "ваш_секретный_ключ_для_refresh"  # Другой ключ для refresh
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Короткое время жизни access токена
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Долгое время жизни refresh токена


# Схемы
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Утилиты
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_tokens(username: str) -> Tuple[str, str]:
    """Создает access и refresh токены"""
    access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = jwt.encode(
        {"sub": username, "type": "access", "exp": datetime.utcnow() + access_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    refresh_token = jwt.encode(
        {"sub": username, "type": "refresh", "exp": datetime.utcnow() + refresh_expires},
        REFRESH_SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token, refresh_token


async def validate_token(token: str, is_refresh: bool = False):
    """Валидация access/refresh токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        secret = REFRESH_SECRET_KEY if is_refresh else SECRET_KEY
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        if payload.get("type") != ("refresh" if is_refresh else "access"):
            raise credentials_exception

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        return TokenData(username=username)
    except JWTError:
        raise credentials_exception


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: Repository = Depends(repository)
):
    """Получение текущего пользователя по access токену"""
    token_data = await validate_token(token)
    safe_user = await repo.user.get_safe_user_by_username(username=token_data.username)
    if safe_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return safe_user


async def authenticate_user(
    username: str,
    password: str,
    repo: Repository
) -> User | bool:
    """
    Аутентификация пользователя по логину и паролю

    :param username: Логин пользователя
    :param password: Введенный пароль (в чистом виде)
    :param repo: Экземпляр репозитория
    :return: Объект User или False если аутентификация не удалась
    """
    # Получаем пользователя из базы
    user = await repo.user.get_user_by_username(username)

    # Если пользователь не найден или пароль не совпадает
    if not user or not pwd_context.verify(password, user.password):
        return False

    return user
