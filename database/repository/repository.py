from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

# сюда импортировать все репозитории
from database.repository import (
    UserRepository,
    EventRepository
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
        self.user: UserRepository = UserRepository(session)
        self.event: EventRepository = EventRepository(session)
        # здесь создавать все репозитории

