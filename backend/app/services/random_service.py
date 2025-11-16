from __future__ import annotations

import random
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Stock
from ..schemas.random_pick import RandomPickResponse


async def pick_random_stock(session: AsyncSession) -> RandomPickResponse:
    stmt = select(Stock).order_by(func.random()).limit(1)
    result = await session.execute(stmt)
    stock = result.scalars().first()
    if not stock:
        raise ValueError("Stock universe is empty")
    grade = random.choice(["NPC", "人上人", "顶级"])
    return RandomPickResponse(code=stock.code, name=stock.name, grade=grade, flags=stock.status_tags or [])

