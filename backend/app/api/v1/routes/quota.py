from fastapi import APIRouter

from ....schemas.quota import QuotaResponse
from ....services.quota_service import get_quota_status

router = APIRouter(prefix="/quota", tags=["quota"])


@router.get("", response_model=QuotaResponse)
async def get_quota():
    return get_quota_status()
