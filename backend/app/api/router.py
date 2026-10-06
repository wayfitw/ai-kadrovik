"""Top-level API router. Domain routers are mounted here block by block."""

from fastapi import APIRouter

from app.api import health

api_router = APIRouter()
api_router.include_router(health.router)
