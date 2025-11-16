from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import List, Optional

import requests

from .data_models import QuoteRecord

logger = logging.getLogger(__name__)


class TongHuaShunClient:
    BASE_URL = "https://d.10jqka.com.cn/v6/line/{prefix}_{code}/01/{year}.js"

    def get_daily_quotes(self, code: str, start: date, end: date) -> List[QuoteRecord]:
        quotes: List[QuoteRecord] = []
        for year in range(start.year, end.year + 1):
            text = self._fetch_year_data(code, year)
            if not text:
                continue
            payload = self._parse_js_payload(text)
            if not payload:
                continue
            for entry in payload.split(";"):
                if not entry.strip():
                    continue
                fields = entry.split(",")
                if len(fields) < 7:
                    continue
                trade_date = datetime.strptime(fields[0], "%Y%m%d").date()
                if trade_date < start or trade_date > end:
                    continue
                quotes.append(
                    QuoteRecord(
                        code=code,
                        trade_date=trade_date,
                        close=self._safe_float(fields[1]),
                        open=self._safe_float(fields[2]),
                        high=self._safe_float(fields[3]),
                        low=self._safe_float(fields[4]),
                        volume=self._safe_float(fields[5]),
                        amount=self._safe_float(fields[6]),
                        turnover=None,
                        adj_close=self._safe_float(fields[1]),
                        flags=[],
                    )
                )
        quotes.sort(key=lambda q: q.trade_date)
        logger.info("Loaded %s THS quote rows for %s", len(quotes), code)
        return quotes

    def _fetch_year_data(self, code: str, year: int) -> Optional[str]:
        prefixes = self._prefixes_for(code)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
            "Referer": "https://finance.10jqka.com.cn/",
        }
        for prefix in prefixes:
            url = self.BASE_URL.format(prefix=prefix, code=code, year=year)
            try:
                response = requests.get(url, timeout=10, headers=headers)
                response.raise_for_status()
                return response.text
            except requests.RequestException:
                continue
        logger.warning("THS data unavailable for %s in %s", code, year)
        return None

    @staticmethod
    def _prefixes_for(code: str) -> List[str]:
        if code.startswith(("60", "68")):
            return ["hs", "sh"]
        if code.startswith(("00", "30")):
            return ["hs", "sz"]
        return ["hs"]

    @staticmethod
    def _parse_js_payload(text: str) -> str:
        start_idx = text.find("(")
        end_idx = text.rfind(")")
        if start_idx == -1 or end_idx == -1:
            return ""
        body = text[start_idx + 1 : end_idx]
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return ""
        return data.get("data", "")

    @staticmethod
    def _safe_float(value: str) -> float:
        value = value.strip()
        if value in {"", "--"}:
            return 0.0
        return float(value)
