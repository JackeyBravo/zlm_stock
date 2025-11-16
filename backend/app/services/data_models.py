from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class StockInfo:
    code: str
    name: str
    exchange: str
    status_tags: List[str]


@dataclass
class QuoteRecord:
    code: str
    trade_date: date
    open: float
    close: float
    high: float
    low: float
    volume: Optional[float]
    amount: Optional[float]
    turnover: Optional[float]
    adj_close: Optional[float]
    flags: List[str]
