from fastapi import APIRouter, Depends, Query

from ....core.deps import get_db_session
from ....schemas.rank import RankResponse
from ....services.ranking_service import get_rankings

router = APIRouter(prefix="/rank", tags=["rankings"])


@router.get("/hot", response_model=RankResponse)
async def get_hot_rank(days: int = Query(10, ge=1, le=30), limit: int = Query(20, ge=1, le=100), session=Depends(get_db_session)):
    return await get_rankings(session, "hot", days, limit)


@router.get("/best", response_model=RankResponse)
async def get_best_rank(
    days: int = Query(10, ge=1, le=30),
    k: int = Query(5, ge=1, le=10),
    limit: int = Query(20, ge=1, le=100),
    session=Depends(get_db_session),
):
    return await get_rankings(session, "best", days, limit, k)


@router.get("/worst", response_model=RankResponse)
async def get_worst_rank(
    days: int = Query(10, ge=1, le=30),
    k: int = Query(5, ge=1, le=10),
    limit: int = Query(20, ge=1, le=100),
    session=Depends(get_db_session),
):
    return await get_rankings(session, "worst", days, limit, k)
