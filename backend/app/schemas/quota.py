from __future__ import annotations

from pydantic import BaseModel


class QuotaResponse(BaseModel):
    guest_remaining: int
    login_remaining: int
    quota_day: str

