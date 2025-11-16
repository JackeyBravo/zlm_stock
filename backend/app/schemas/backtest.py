from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class BacktestItemSchema(BaseModel):
    code: str
    name: str
    buy_date: date
    buy_price: float
    sell_date: date
    sell_price: float
    ret: float
    excess: float
    ann: float
    sharpe: Optional[float] = None
    mdd: Optional[float] = None
    calmar: Optional[float] = None
    score: Optional[float] = None
    grade: Optional[str] = None
    flags: List[str] = Field(default_factory=list)


class EquityPoint(BaseModel):
    date: date
    portfolio_nv: float
    bench_nv: float


class BacktestSummary(BaseModel):
    win_rate: float
    ret: float
    ann: float
    bench_ret: float
    bench_ann: float
    excess: float
    sharpe: Optional[float] = None
    mdd: Optional[float] = None
    calmar: Optional[float] = None


class BacktestWindow(BaseModel):
    start: date
    end: date
    trading_days: int


class BacktestResponse(BaseModel):
    bt_id: str
    window: BacktestWindow
    benchmark: str
    summary: BacktestSummary
    equity: List[EquityPoint]
    items: List[BacktestItemSchema]


class BacktestRequest(BaseModel):
    stocks: List[str]
    recommend_date: date
    end_date: Optional[date] = None
    benchmark: str = "HS300"
    price_adjust: str = "post"


class BacktestListResponse(BaseModel):
    items: List[BacktestResponse]

