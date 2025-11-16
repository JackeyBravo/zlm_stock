import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine

from ..core.config import get_settings
from .base import Base
from . import models  # noqa: F401

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Create database tables based on ORM models."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    logger.info("Database initialized using %s", settings.database_url)


if __name__ == "__main__":
    asyncio.run(init_db())
