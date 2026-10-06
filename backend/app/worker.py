"""Celery application: workers (timers, obligations) and beat (daily schedules).

Periodic tasks are registered here block by block (2.5, 3.1, 3.3). The schedule is
intentionally empty in block 1.1 — only a ``ping`` task proves the wiring.
"""

from celery import Celery

from app.core.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "kadrovik",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[],
)
celery_app.conf.update(
    timezone="Europe/Moscow",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={},
)


@celery_app.task(name="app.ping")
def ping() -> str:
    return "pong"
