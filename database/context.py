from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database import database_init, db_settings


@asynccontextmanager
async def db_session(async_session_maker: async_sessionmaker[AsyncSession]):
    """Контекстный менеджер для работы с сессией."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def repository():
    """Контекстный менеджер для работы с репозиторием."""
    from database.repository.repository import Repository  # Импорт здесь, чтобы избежать циклических зависимостей

    async with db_session(database_init(db_settings)) as session:
        yield Repository(session)
