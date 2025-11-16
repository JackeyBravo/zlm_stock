from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Date, DateTime, Float, Integer, JSON, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Stock(Base):
    __tablename__ = "stocks"

    code: Mapped[str] = mapped_column(String(12), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    exchange: Mapped[str] = mapped_column(String(16))
    status_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QuoteDaily(Base):
    __tablename__ = "quotes_daily"

    code: Mapped[str] = mapped_column(String(12), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    open: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    turnover: Mapped[float | None] = mapped_column(Float, nullable=True)
    adj_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    flags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Backtest(Base):
    __tablename__ = "backtest"

    bt_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    start: Mapped[date] = mapped_column(Date)
    end: Mapped[date] = mapped_column(Date)
    benchmark: Mapped[str] = mapped_column(String(16))
    summary_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[List["BacktestItem"]] = relationship(back_populates="backtest", cascade="all, delete-orphan")


class BacktestItem(Base):
    __tablename__ = "backtest_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bt_id: Mapped[str] = mapped_column(String(36), ForeignKey("backtest.bt_id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(12))
    name: Mapped[str] = mapped_column(String(64))
    buy_date: Mapped[date] = mapped_column(Date)
    buy_price: Mapped[float] = mapped_column(Float)
    sell_date: Mapped[date] = mapped_column(Date)
    sell_price: Mapped[float] = mapped_column(Float)
    ret: Mapped[float] = mapped_column(Float)
    excess: Mapped[float] = mapped_column(Float)
    ann: Mapped[float] = mapped_column(Float)
    sharpe: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mdd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calmar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    flags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    backtest: Mapped["Backtest"] = relationship(back_populates="items")
