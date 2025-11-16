from __future__ import annotations

from datetime import date, timedelta
from typing import List

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Backtest, BacktestItem
from ..schemas.rank import RankItem, RankResponse


async def get_rankings(
    session: AsyncSession, rank_type: str, days: int = 10, limit: int = 20, k: int = 5
) -> RankResponse:
    cutoff = date.today() - timedelta(days=days)
    base_query = (
        select(
            BacktestItem.code,
            BacktestItem.name,
            func.count().label("runs"),
            func.avg(BacktestItem.ret).label("avg_ret"),
            func.avg(BacktestItem.score).label("avg_score"),
        )
        .join(Backtest, BacktestItem.bt_id == Backtest.bt_id)
        .where(Backtest.start >= cutoff)
        .group_by(BacktestItem.code, BacktestItem.name)
    )

    if rank_type == "hot":
        stmt = base_query.order_by(func.count().desc()).limit(limit)
    elif rank_type == "best":
        stmt = base_query.order_by(func.avg(BacktestItem.score).desc()).limit(limit)
    elif rank_type == "worst":
        stmt = base_query.order_by(func.avg(BacktestItem.ret).asc()).limit(limit)
    else:
        raise ValueError("Unsupported rank type")

    result = await session.execute(stmt)
    items = [
        RankItem(
            code=row.code,
            name=row.name,
            score=row.avg_score,
            reason=f"近{days}日回测{int(row.runs)}次，平均收益 {row.avg_ret:.2%}",
        )
        for row in result.all()
    ]

    return RankResponse(type=rank_type, days=days, k=k if rank_type != "hot" else None, limit=limit, items=items)

