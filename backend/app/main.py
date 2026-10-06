"""FastAPI application factory."""

from fastapi import FastAPI

from app import __version__
from app.api.router import api_router
from app.core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        docs_url="/docs" if settings.app_env != "prod" else None,
        redoc_url=None,
    )
    app.include_router(api_router)
    return app


app = create_app()
