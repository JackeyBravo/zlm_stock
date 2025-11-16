from __future__ import annotations

from datetime import date

from ..core.config import get_settings
from ..schemas.quota import QuotaResponse


def get_quota_status() -> QuotaResponse:
    today = date.today().isoformat()
    settings = get_settings()
    return QuotaResponse(
        guest_remaining=settings.quota_guest_per_day,
        login_remaining=settings.quota_login_per_day,
        quota_day=today,
    )

