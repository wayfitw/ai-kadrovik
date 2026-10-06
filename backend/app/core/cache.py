"""Redis client (broker for Celery, cache / locks for the API)."""

from functools import lru_cache

from redis import Redis

from app.core.settings import get_settings


@lru_cache
def get_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, socket_connect_timeout=2, socket_timeout=2)
