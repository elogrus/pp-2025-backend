import uuid

from loguru import logger
import sqlalchemy as sa
from database.repository import BaseRepository
from uuid import UUID
from typing import Optional, Any
from database.models import User


class UserRepository(BaseRepository):

    async def create_user(self,
        login: str,
        password: str
    ) -> None:
        """
        Создаёт в бд нового юзера.

        :param login: логин юзера
        :param password: пароль юзера
        :return:
        """
        user_id = uuid.uuid4()
        if (await self.get(user_id)) is None:
            user = User(id=user_id, login=login, password=hash(password))
            self._session.add(user)

    async def get(self, user_id: UUID) -> "Optional[User]":
        """

        :param user_id: Айдишник юзера в бд.
        :return: Модель User
        """
        query = sa.select(User).where(User.id == user_id)
        return await self._session.scalar(query)

    async def update(
        self,
        user_id: UUID,
        **fields: Any,
    ) -> None:

        query = sa.update(User).where(User.id == user_id).values(**fields)
        await self._session.execute(query)
        await self._session.flush()

    async def is_has_any_role(
        self,
        user_id: UUID,
        roles  # : "list[Union[RoleEnum, str]]",
    ) -> bool:
        """
        Имеет ли юзер хотя бы одну роль из переданных.

        :param user_id: ТГ Айди юзера.
        :param roles: Список ролей.
        :return: Тру или фэлс.
        """
        if (user := await self.get(user_id)) is None:
            return False
        """Создать Enum ролей и дописать проверку"""
        # role_names = [role.value if isinstance(role, Enum) else role for role in roles]
        # return any(role.role in role_names for role in user.roles)
