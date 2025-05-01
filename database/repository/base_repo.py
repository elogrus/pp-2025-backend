import uuid
from abc import ABC
from typing import TYPE_CHECKING, TypeVar, Optional, Any, Sequence

from sqlalchemy.engine.result import _TP

from database import database_init, db_settings
from database.models import User

if TYPE_CHECKING:
    import sqlalchemy as sa
    from sqlalchemy import Select, Row
    from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")
M = TypeVar("M")  # Для моделей SQLAlchemy


class BaseRepository(ABC):
    """Базовый класс для репозиториев, нужен для переиспользования кода."""

    _session: Optional["AsyncSession"]

    def __init__(self, session: "AsyncSession") -> None:
        self._session = session

    async def scalar(self, query: "Select[T]") -> Optional[T]:
        """Выполняет scalar запрос."""
        return await self._session.scalar(query)

    async def scalars(self, query: "Select[M]") -> list[M]:
        """Выполняет scalars запрос и возвращает список моделей."""
        result = await self._session.scalars(query)
        return list(result.all())

    async def scalars_multi(self, query: "Select[tuple[M, ...]]"):
        """Для запросов, возвращающих несколько сущностей."""
        result = await self._session.execute(query)
        return result.all()  # list[tuple[...]]

    async def execute(self, query: "Select | Update | Delete") -> Any:
        """Выполняет произвольный запрос."""
        return await self._session.execute(query)

    async def commit(self) -> None:
        """Фиксирует изменения."""
        await self._session.commit()

    async def refresh(self, instance: object) -> None:
        """Обновляет состояние объекта из БД."""
        await self._session.refresh(instance)

    async def merge(self, instance: object) -> None:
        """Добавляет объект в сессию (если не отслеживается)."""
        await self._session.merge(instance)

    async def select_query_to_list(self, query: "Select[tuple[T]]") -> list[T]:
        return list((await self._session.scalars(query)).all())


