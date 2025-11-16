from __future__ import annotations

import math
import statistics
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, List, Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import Backtest, BacktestItem, QuoteDaily, Stock
from ..schemas.backtest import (
    BacktestItemSchema,
    BacktestRequest,
    BacktestResponse,
    BacktestSummary,
    BacktestWindow,
    EquityPoint,
)
from .ths_client import TongHuaShunClient
from .data_models import QuoteRecord

ANNUAL_TRADING_DAYS = 244


@dataclass
class ItemCalcResult:
    code: str
    name: str
    buy_date: date
    buy_price: float
    sell_date: date
    sell_price: float
    ret: float
    ann: float
    sharpe: float | None
    mdd: float | None
    calmar: float | None
    score: float | None
    grade: str | None
    flags: List[str]
    trading_days: int


async def run_backtest(session: AsyncSession, payload: BacktestRequest) -> BacktestResponse:
    if not payload.stocks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入至少一只股票或代码")
    if len(payload.stocks) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="一次最多回测 20 只股票")

    window_end = payload.end_date or date.today()
    if window_end <= payload.recommend_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="结束日期需晚于推荐日期")

    stocks = await _resolve_stocks(session, payload.stocks)
    if not stocks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到可回测的股票代码")

    item_results: List[ItemCalcResult] = []
    for stock in stocks:
        quotes = await _load_quotes(session, stock.code, payload.recommend_date, window_end)
        if not quotes:
            continue
        result = _calculate_for_stock(stock, quotes, payload.recommend_date, window_end)
        if result:
            item_results.append(result)

    if not item_results:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="所选股票区间缺少行情数据")

    summary = _aggregate_summary(item_results)
    bt_id = str(uuid.uuid4())
    backtest = Backtest(
        bt_id=bt_id,
        start=payload.recommend_date,
        end=window_end,
        benchmark=payload.benchmark,
        summary_json=summary.model_dump(),
    )
    for item in item_results:
        backtest.items.append(
            BacktestItem(
                bt_id=bt_id,
                code=item.code,
                name=item.name,
                buy_date=item.buy_date,
                buy_price=item.buy_price,
                sell_date=item.sell_date,
                sell_price=item.sell_price,
                ret=item.ret,
                excess=item.ret - summary.bench_ret,
                ann=item.ann,
                sharpe=item.sharpe,
                mdd=item.mdd,
                calmar=item.calmar,
                score=item.score,
                grade=item.grade,
                flags=item.flags,
            )
        )

    session.add(backtest)
    await session.commit()
    loaded = await _load_backtest(session, bt_id)
    return _serialize_backtest(loaded)


async def get_backtest_response(session: AsyncSession, bt_id: str) -> BacktestResponse:
    backtest = await _load_backtest(session, bt_id)
    if not backtest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回测不存在")
    return _serialize_backtest(backtest)


async def _load_backtest(session: AsyncSession, bt_id: str) -> Backtest | None:
    stmt = select(Backtest).options(selectinload(Backtest.items)).where(Backtest.bt_id == bt_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def _resolve_stocks(session: AsyncSession, tokens: Sequence[str]) -> List[Stock]:
    resolved: List[Stock] = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        stock = None
        normalized = _normalize_code(token)
        if normalized:
            stock = await session.get(Stock, normalized)
        if not stock:
            stmt = select(Stock).where(Stock.name == token).limit(1)
            result = await session.execute(stmt)
            stock = result.scalars().first()
        if stock:
            resolved.append(stock)
    return resolved


def _normalize_code(token: str) -> str | None:
    digits = "".join(ch for ch in token if ch.isdigit())
    if not digits:
        return None
    if len(digits) <= 6:
        return digits.zfill(6)
    return digits


@dataclass
class QuoteView:
    date: date
    open: float
    close: float
    high: float
    low: float
    volume: float | None
    amount: float | None
    turnover: float | None
    adj_close: float | None
    flags: List[str]


async def _load_quotes(session: AsyncSession, code: str, start: date, end: date) -> List[QuoteView]:
    stmt = (
        select(QuoteDaily)
        .where(QuoteDaily.code == code, QuoteDaily.date >= start, QuoteDaily.date <= end)
        .order_by(QuoteDaily.date.asc())
    )
    result = await session.execute(stmt)
    records = list(result.scalars().all())
    if records:
        return [_to_quote_view(r) for r in records]
    ths_client = TongHuaShunClient()
    return [_to_quote_view(r) for r in ths_client.get_daily_quotes(code, start, end)]


def _to_quote_view(obj: QuoteRecord | QuoteDaily) -> QuoteView:
    return QuoteView(
        date=getattr(obj, "date", getattr(obj, "trade_date")),
        open=obj.open,
        close=obj.close,
        high=obj.high,
        low=obj.low,
        volume=obj.volume,
        amount=getattr(obj, "amount", None),
        turnover=getattr(obj, "turnover", None),
        adj_close=getattr(obj, "adj_close", obj.close),
        flags=getattr(obj, "flags", []) or [],
    )


def _calculate_for_stock(stock: Stock, quotes: List[QuoteDaily], recommend_date: date, window_end: date) -> ItemCalcResult | None:
    buy_quote = next((q for q in quotes if q.date > recommend_date), quotes[0])
    sell_quote = next((q for q in reversed(quotes) if q.date <= window_end), quotes[-1])
    if buy_quote.date >= sell_quote.date:
        return None

    buy_price = buy_quote.open
    sell_price = sell_quote.close
    if buy_price <= 0 or sell_price <= 0:
        return None

    ret = sell_price / buy_price - 1
    trading_days = max(1, (sell_quote.date - buy_quote.date).days)
    ann = annualize(ret, trading_days)

    daily_returns = _calc_daily_returns(quotes)
    sharpe = calc_sharpe(daily_returns)
    mdd = calc_max_drawdown(quotes, buy_price)
    calmar = calc_calmar(ann, mdd)
    score = calc_score(ann, sharpe, mdd)
    grade = classify_grade(ann)

    flags: List[str] = []
    if trading_days < 2:
        flags.append("SHORT_WINDOW")
    return ItemCalcResult(
        code=stock.code,
        name=stock.name,
        buy_date=buy_quote.date,
        buy_price=round(buy_price, 4),
        sell_date=sell_quote.date,
        sell_price=round(sell_price, 4),
        ret=ret,
        ann=ann,
        sharpe=sharpe,
        mdd=mdd,
        calmar=calmar,
        score=score,
        grade=grade,
        flags=flags,
        trading_days=trading_days,
    )


def _aggregate_summary(items: List[ItemCalcResult]) -> BacktestSummary:
    win_rate = sum(1 for item in items if item.ret > 0) / len(items)
    avg_ret = statistics.mean(item.ret for item in items)
    avg_ann = statistics.mean(item.ann for item in items)
    avg_sharpe = statistics.mean([item.sharpe for item in items if item.sharpe is not None]) if any(
        item.sharpe is not None for item in items
    ) else None
    avg_mdd = statistics.mean([item.mdd for item in items if item.mdd is not None]) if any(
        item.mdd is not None for item in items
    ) else None
    avg_calmar = statistics.mean([item.calmar for item in items if item.calmar is not None]) if any(
        item.calmar is not None for item in items
    ) else None

    bench_ret = 0.0
    bench_ann = 0.0
    excess = avg_ret - bench_ret

    return BacktestSummary(
        win_rate=win_rate,
        ret=avg_ret,
        ann=avg_ann,
        bench_ret=bench_ret,
        bench_ann=bench_ann,
        excess=excess,
        sharpe=avg_sharpe,
        mdd=avg_mdd,
        calmar=avg_calmar,
    )


def _serialize_backtest(bt: Backtest) -> BacktestResponse:
    items = [
        BacktestItemSchema(
            code=item.code,
            name=item.name,
            buy_date=item.buy_date,
            buy_price=item.buy_price,
            sell_date=item.sell_date,
            sell_price=item.sell_price,
            ret=item.ret,
            excess=item.excess,
            ann=item.ann,
            sharpe=item.sharpe,
            mdd=item.mdd,
            calmar=item.calmar,
            score=item.score,
            grade=item.grade,
            flags=item.flags or [],
        )
        for item in bt.items
    ]
    summary = BacktestSummary(**bt.summary_json)
    window = BacktestWindow(
        start=bt.start,
        end=bt.end,
        trading_days=(bt.end - bt.start).days,
    )
    equity = [
        EquityPoint(date=window.start, portfolio_nv=1.0, bench_nv=1.0),
        EquityPoint(date=window.end, portfolio_nv=1.0 + summary.ret, bench_nv=1.0 + summary.bench_ret),
    ]
    return BacktestResponse(
        bt_id=bt.bt_id,
        window=window,
        benchmark=bt.benchmark,
        summary=summary,
        equity=equity,
        items=items,
    )


def _calc_daily_returns(quotes: List[QuoteDaily]) -> List[float]:
    returns: List[float] = []
    for prev, curr in zip(quotes, quotes[1:]):
        if prev.close > 0:
            returns.append(curr.close / prev.close - 1)
    return returns


def annualize(ret: float, trading_days: int) -> float:
    if trading_days <= 0:
        return 0.0
    factor = ANNUAL_TRADING_DAYS / max(1, trading_days)
    return (1 + ret) ** factor - 1


def calc_sharpe(daily_returns: List[float]) -> float | None:
    if len(daily_returns) < 2:
        return None
    mean = statistics.mean(daily_returns)
    stdev = statistics.stdev(daily_returns)
    if stdev == 0:
        return None
    return (mean / stdev) * math.sqrt(ANNUAL_TRADING_DAYS)


def calc_max_drawdown(quotes: List[QuoteDaily], base_price: float) -> float | None:
    if not quotes:
        return None
    peak = base_price
    max_drawdown = 0.0
    for quote in quotes:
        value = quote.close
        if value > peak:
            peak = value
        drawdown = (value - peak) / peak
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    return max_drawdown


def calc_calmar(ann: float, mdd: float | None) -> float | None:
    if mdd is None or mdd == 0:
        return None
    return ann / abs(mdd)


def calc_score(ann: float, sharpe: float | None, mdd: float | None) -> float | None:
    parts = []
    if ann is not None:
        parts.append(0.5 * ann)
    if sharpe is not None:
        parts.append(0.3 * sharpe)
    if mdd is not None:
        parts.append(-0.2 * abs(mdd))
    if not parts:
        return None
    return sum(parts)


def classify_grade(ann: float) -> str:
    thresholds = [
        (0.25, "秀"),
        (0.15, "顶级"),
        (0.05, "人上人"),
        (0.0, "NPC"),
    ]
    for threshold, label in thresholds:
        if ann >= threshold:
            return label
    return "拉完了"
