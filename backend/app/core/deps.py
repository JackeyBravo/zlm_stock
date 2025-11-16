from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings

settings = get_settings()
if settings.database_url.startswith("sqlite"):
    db_path = settings.database_url.split("///")[-1]
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

_engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionMaker = async_sessionmaker(_engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionMaker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_settings_dep():
    return get_settings()
