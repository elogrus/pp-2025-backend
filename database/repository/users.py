from loguru import logger
import sqlalchemy as sa
from sqlalchemy import select

from database.repository.base_repo import BaseRepository
from typing import Optional, List
from database.models import User, SafeUser


class UserRepository(BaseRepository):

    async def create_user(
        self,
        username: str,
        nickname: str,
        password: str
    ) -> SafeUser:
        """
        Создаёт в бд нового юзера.

        :param username: Логин юзера.
        :param nickname: Никнейм юзера.
        :param password: пароль юзера.
        :return User: модель User.
        """
        user = User(username=username, nickname=nickname, password=password)
        self._session.add(user)
        await self.commit()
        await self.refresh(user)
        safe_user = SafeUser(username=username, nickname=nickname)
        safe_user.user_id = user.user_id
        logger.info("Новый пользователь {user}", user=user)
        self._session.add(safe_user)
        await self.commit()
        await self.refresh(safe_user)
        return safe_user

    async def get(self, user_id: int) -> Optional[SafeUser]:
        """
        Возвращает пользователя.

        :param user_id: Айдишник пользователя в бд.
        :return: Модель User
        """
        query = sa.select(SafeUser).where(SafeUser.user_id == user_id)
        return await self.scalar(query)

    async def get_by_limit(self, limit: int) -> Optional[List[SafeUser]]:
        """
        Позже сделать перегрузки этой функции для фильтрации запросов в бд.
        Возвращает первые limit юзеров из бд
        :param limit:
        :return List[User] | None:
        """
        query = sa.select(SafeUser).limit(limit)
        return await self.scalars(query)

    async def update_username_to_db(
        self,
        user_id: int,
        nickname: str,
    ) -> None:
        """
        Сохраняет пользователя в базе данных.

        Если пользователь уже существует, то обновляет никнейм,

        :param user_id: Айди юзера.
        :param nickname: Имя пользователя.
        """

        if (safe_user := await self.get(user_id)) is None:
            safe_user.nickname = nickname
        query = sa.select(User).where(User.user_id == user_id)
        user = await self.scalar(query)
        user.nickname = nickname
        await self._session.flush()  # Можно сделать валидацию данных перед коммитом
        await self.commit()
        await self.refresh(safe_user)
        await self.refresh(user)

    async def get_user_by_username(self, username: str) -> User:
        """
        Получить юзера по username, пользоваться только при авторизации!
        :param username: Username юзера
        :return User: Модель юзера
        """
        query = sa.select(User).where(User.username == username)
        return await self.scalar(query)

    async def get_safe_user_by_username(self, username: str) -> SafeUser:
        """
        Получить юзера по username.
        :param username: Username юзера
        :return SafeUser: Модель безопасного юзера
        """
        query = sa.select(SafeUser).where(SafeUser.username == username)
        return await self.scalar(query)


    # async def is_has_any_role(
    #     self,
    #     user_id: int,
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
    #     """Создать Enum ролей и переписать проверку"""
    #     # role_names = [role.value if isinstance(role, Enum) else role for role in roles]
    #     # return any(role.role in role_names for role in user.roles)
    #
