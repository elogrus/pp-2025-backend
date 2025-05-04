from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database import database_init
from database.db_settings import db_settings


@asynccontextmanager
async def db_session(async_session_maker: async_sessionmaker[AsyncSession]):
    """Контекстный менеджер для работы с сессией."""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        await session.close()
        logger.debug("Session closed properly")


@asynccontextmanager
async def repository_manager():
    """Контекстный менеджер для работы с репозиторием."""
    from database.repository.repository import Repository  # Импорт здесь, чтобы избежать циклических зависимостей
    async with db_session(await database_init(db_settings)) as session:
        yield Repository(session)


async def repository():
    async with repository_manager() as repo:
        yield repo
