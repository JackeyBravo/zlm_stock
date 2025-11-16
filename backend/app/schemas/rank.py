from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class RankItem(BaseModel):
    code: str
    name: str
    score: Optional[float] = None
    grade: Optional[str] = None
    reason: Optional[str] = None


class RankResponse(BaseModel):
    type: str
    days: int
    k: Optional[int] = None
    limit: int
    updated_at: Optional[date] = None
    items: List[RankItem]

