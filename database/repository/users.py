import uuid

from loguru import logger
import sqlalchemy as sa
from database.repository.base_repo import BaseRepository
from uuid import UUID
from typing import Optional, Any
from database.models import User


class UserRepository(BaseRepository):

    async def create_user(
        self,
        username: str,
        login: str,
        __password: str
    ) -> None:
        """
        Создаёт в бд нового юзера.

        :param username: Никнейм юзера.
        :param login: логин юзера.
        :param __password: пароль юзера.
        :return None:
        """
        user_id = str(uuid.uuid4())
        if (user := await self.get(user_id)) is None:
            user = User(user_id=user_id, username=username, login=login, password=hash(__password))
            self._session.add(user)
            await self.commit()
            await self.refresh(user)
            logger.info("Новый пользователь {user}", user=user)
        elif user.should_be_updated(username):
            ...  # обновить данные юзера или же выдать ошибку валидации, что уже существует такой юзер

    async def get(self, user_id: str) -> "Optional[User]":
        """
        Возвращает пользователя.

        :param user_id: Айдишник пользователя в бд.
        :return: Модель User
        """
        query = sa.select(User).where(User.user_id == user_id)
        return await self.scalar(query)

    async def update_username_to_db(
        self,
        user_id: str,
        username: str,
    ) -> None:
        """
        Сохраняет пользователя в базе данных.

        Если пользователь уже существует, то обновляет никнейм,

        :param user_id: Айди юзера.
        :param username: Имя пользователя.
        """

        if (user := await self.get(user_id)) is None:
            user.username = username

        await self._session.flush() # Можно сделать валидацию данных перед коммитом
        await self.commit()
        await self.refresh(user)

    # async def is_has_any_role(
    #     self,
    #     user_id: UUID,
    #     roles  # : "list[Union[RoleEnum, str]]",
    # ) -> bool:
    #     """
    #     Имеет ли юзер хотя бы одну роль из переданных.
    #
    #     :param user_id: ТГ Айди юзера.
    #     :param roles: Список ролей.
    #     :return: Тру или фэлс.
    #     """
    #     if (user := await self.get(user_id)) is None:
    #         return False
    #     """Создать Enum ролей и дописать проверку"""
    #     # role_names = [role.value if isinstance(role, Enum) else role for role in roles]
    #     # return any(role.role in role_names for role in user.roles)
    #
