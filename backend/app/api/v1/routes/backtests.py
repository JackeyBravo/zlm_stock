from fastapi import APIRouter, Depends

from ....core.deps import get_db_session
from ....schemas.backtest import BacktestRequest, BacktestResponse
from ....services.backtest_engine import get_backtest_response, run_backtest

router = APIRouter(tags=["backtest"])


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest_endpoint(payload: BacktestRequest, session=Depends(get_db_session)):
    return await run_backtest(session, payload)


@router.get("/backtest/{bt_id}", response_model=BacktestResponse)
async def get_backtest_endpoint(bt_id: str, session=Depends(get_db_session)):
    return await get_backtest_response(session, bt_id)
