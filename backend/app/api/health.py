"""Health / readiness endpoints."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app import __version__
from app.core.cache import get_redis
from app.core.db import get_engine
from app.core.settings import get_settings

router = APIRouter(tags=["health"])

CheckStatus = Literal["ok", "error"]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    env: str
    checks: dict[str, CheckStatus]


def _check_db() -> CheckStatus:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:  # noqa: BLE001 — any failure means "not ready"
        return "error"


def _check_redis() -> CheckStatus:
    try:
        return "ok" if get_redis().ping() else "error"
    except Exception:  # noqa: BLE001
        return "error"


@router.get("/health/live", summary="Liveness: process is up")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health", response_model=HealthResponse, summary="Readiness: DB and Redis reachable")
def health() -> HealthResponse:
    checks: dict[str, CheckStatus] = {"db": _check_db(), "redis": _check_redis()}
    status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return HealthResponse(
        status=status, version=__version__, env=get_settings().app_env, checks=checks
    )
