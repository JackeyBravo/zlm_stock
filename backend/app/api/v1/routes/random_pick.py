from fastapi import APIRouter, Depends

from ....core.deps import get_db_session
from ....schemas.random_pick import RandomPickResponse
from ....services.random_service import pick_random_stock

router = APIRouter(prefix="/random", tags=["random"])


@router.get("", response_model=RandomPickResponse)
async def pick_random_stock_endpoint(session=Depends(get_db_session)):
    return await pick_random_stock(session)
