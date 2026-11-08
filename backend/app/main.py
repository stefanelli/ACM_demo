"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.v1.market import router as market_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Application factory for the Aloe backend."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Fed meeting-curve research and paper-trading platform (mock-data scaffold).",
    )

    app.include_router(market_router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
