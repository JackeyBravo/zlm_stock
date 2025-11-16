from __future__ import annotations

import logging

import akshare as ak
import pandas as pd

from .data_models import QuoteRecord, StockInfo

logger = logging.getLogger(__name__)


class AkShareClient:
    """Wrapper around AKShare for endpoints仍可访问的场景（主要用于证券列表）。"""

    def list_a_stocks(self) -> list[StockInfo]:
        df = ak.stock_info_a_code_name()
        records: list[StockInfo] = []
        for _, row in df.iterrows():
            code = str(row["code"]).zfill(6)
            name = str(row["name"]).strip()
            exchange = self._detect_exchange(code)
            records.append(StockInfo(code=code, name=name, exchange=exchange, status_tags=[]))
        logger.info("Loaded %s A-share symbols from AKShare", len(records))
        return records

    @staticmethod
    def _detect_exchange(code: str) -> str:
        if code.startswith(("60", "68")):
            return "SSE"
        if code.startswith(("00", "30")):
            return "SZSE"
        if code.startswith("43"):
            return "BSE"
        return "UNKNOWN"
