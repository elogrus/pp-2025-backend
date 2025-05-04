from loguru import logger
import sqlalchemy as sa

from database.repository.base_repo import BaseRepository
from typing import Optional, List
from database.models import User


class UserRepository(BaseRepository):

    async def create_user(
        self,
        username: str,
        login: str,
        password: str
    ) -> User:
        """
        Создаёт в бд нового юзера.

        :param username: Никнейм юзера.
        :param login: логин юзера.
        :param password: пароль юзера.
        :return User: модель User.
        """
        user = User(username=username, login=login, password=password)
        self._session.add(user)
        await self.commit()
        await self.refresh(user)
        logger.info("Новый пользователь {user}", user=user)
        return user

    async def get(self, user_id: int) -> Optional[User]:
        """
        Возвращает пользователя.

        :param user_id: Айдишник пользователя в бд.
        :return: Модель User
        """
        query = sa.select(User).where(User.user_id == user_id)
        return await self.scalar(query)

    async def get_by_limit(self, limit: int) -> Optional[List[User]]:
        """
        Позже сделать перегрузки этой функции для фильтрации запросов в бд.
        Возвращает первые limit юзеров из бд
        :param limit:
        :return List[User] | None:
        """
        query = sa.select(User).limit(limit)
        return await self.scalars(query)

    async def update_username_to_db(
        self,
        user_id: int,
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

        await self._session.flush()  # Можно сделать валидацию данных перед коммитом
        await self.commit()
        await self.refresh(user)

    async def get_by_login(self, login: str) -> User:
        """
        Получить юзера по логину.
        :param login: Логин юзера
        :return User: Модель юзера
        """
        query = sa.select(User).where(User.login == login)
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
