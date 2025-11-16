from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import SessionMaker
from ..db.models import QuoteDaily, Stock
from .akshare_client import AkShareClient
from .data_models import QuoteRecord, StockInfo
from .ths_client import TongHuaShunClient

logger = logging.getLogger(__name__)


async def sync_stock_master() -> None:
    client = AkShareClient()
    stocks = client.list_a_stocks()
    async with SessionMaker() as session:
        await _upsert_stocks(session, stocks)
        await session.commit()
    logger.info("Stock master sync completed")


async def sync_quotes_for_codes(codes: Sequence[str], start: date, end: date) -> None:
    client = TongHuaShunClient()
    async with SessionMaker() as session:
        for code in codes:
            try:
                quotes = client.get_daily_quotes(code, start, end)
                await _upsert_quotes(session, quotes)
                await session.commit()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to sync quotes for %s: %s", code, exc)
    logger.info("Quote sync completed for %s codes", len(codes))


async def _upsert_stocks(session: AsyncSession, stocks: Iterable[StockInfo]) -> None:
    for stock in stocks:
        existing = await session.get(Stock, stock.code)
        if existing:
            existing.name = stock.name
            existing.exchange = stock.exchange
            existing.status_tags = stock.status_tags
        else:
            session.add(
                Stock(
                    code=stock.code,
                    name=stock.name,
                    exchange=stock.exchange,
                    status_tags=stock.status_tags,
                )
            )


async def _upsert_quotes(session: AsyncSession, quotes: Iterable[QuoteRecord]) -> None:
    for quote in quotes:
        existing = await session.get(QuoteDaily, (quote.code, quote.trade_date))
        if existing:
            existing.open = quote.open
            existing.close = quote.close
            existing.high = quote.high
            existing.low = quote.low
            existing.volume = quote.volume
            existing.amount = quote.amount
            existing.turnover = quote.turnover
            existing.adj_close = quote.adj_close
            existing.flags = quote.flags
        else:
            session.add(
                QuoteDaily(
                    code=quote.code,
                    date=quote.trade_date,
                    open=quote.open,
                    close=quote.close,
                    high=quote.high,
                    low=quote.low,
                    volume=quote.volume,
                    amount=quote.amount,
                    turnover=quote.turnover,
                    adj_close=quote.adj_close,
                    flags=quote.flags,
                )
            )


async def list_known_codes(limit: int = 20) -> list[str]:
    async with SessionMaker() as session:
        stmt = select(Stock.code).limit(limit)
        result = await session.execute(stmt)
        return [row[0] for row in result.all()]


if __name__ == "__main__":
    async def _demo():
        await sync_stock_master()
        codes = await list_known_codes(limit=5)
        await sync_quotes_for_codes(codes, date(2025, 1, 1), date(2025, 1, 10))

    asyncio.run(_demo())
