from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from database.repository import (
    UserRepository,
# сюда импортировать все репозитории
)
from database.repository.base_repo import BaseRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Repository(BaseRepository):
    """Класс для вызова функций работы с базой данных."""

    def __init__(
        self,
        session: "AsyncSession",
    ) -> None:
        super().__init__(session)
        self.user = UserRepository(session)
        # здесь создавать все репозитории

    async def update_username_to_db(
        self,
        user_id: str,
        username: str,
    ) -> None:
        """
        Обновление никнейма пользователя.

        :param user_id: Айди пользователя.
        :param username: Имя пользователя.
        """
        await self.user.update_username_to_db(user_id, username)

