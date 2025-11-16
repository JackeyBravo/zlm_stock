from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class RandomPickResponse(BaseModel):
    code: str
    name: str
    grade: Optional[str] = None
    reason: Optional[str] = None
    flags: List[str] = []

