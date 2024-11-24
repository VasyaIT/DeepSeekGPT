from contextlib import asynccontextmanager
from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from bot.config.config_db import config_db


engine = create_async_engine(config_db.database_url, future=True)
session_factory = async_scoped_session(
    async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False), scopefunc=current_task
)


@asynccontextmanager
async def db_session():
    session: AsyncSession = session_factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
