from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import URL, MetaData, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.base import AlchemyBaseModel

if TYPE_CHECKING:
    from database.db_settings import DBSettings


__all__ = (
    "AlchemyBaseModel",
    "database_init",
)


@logger.catch(reraise=True)
async def database_init(db_setting: "DBSettings") -> async_sessionmaker[AsyncSession]:
    """
    Иницализация подключения к базе данных.

    :param db_settings: Настройки базы данных.
    :return: Асинхронный делатель сессий. :)
    """
    database_url = URL.create(
        drivername="postgresql+asyncpg",
        username=db_setting.user,
        password=db_setting.password,
        host=db_setting.host,
        port=db_setting.host_port,
        database=db_setting.db,
    )
    async_engine = create_async_engine(
        database_url,
        echo=True,
    )

    # Проверка подключения к базе данных
    async with async_engine.begin():
        pass

    # Создание моделей в бд. Разовая акция :)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(AlchemyBaseModel.metadata.drop_all)
    #     await conn.run_sync(AlchemyBaseModel.metadata.create_all)

    return async_sessionmaker(
        bind=async_engine,
        autoflush=False,
        future=True,
        expire_on_commit=False,
    )


