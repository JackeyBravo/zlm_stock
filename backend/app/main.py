from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.routes.backtests import router as backtest_router
from .api.v1.routes.quota import router as quota_router
from .api.v1.routes.rankings import router as ranking_router
from .api.v1.routes.random_pick import router as random_router
from .core.config import get_settings
from .core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(title=settings.project_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.api_v1_prefix
    app.include_router(backtest_router, prefix=api_prefix)
    app.include_router(ranking_router, prefix=api_prefix)
    app.include_router(random_router, prefix=api_prefix)
    app.include_router(quota_router, prefix=api_prefix)

    @app.get("/healthz", tags=["health"])
    async def healthz():
        return {"status": "ok"}

    return app


app = create_app()

