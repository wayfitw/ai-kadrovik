"""SQLAlchemy 2 engine, session factory and declarative base.

Two engines exist on purpose (see CLAUDE.md, principle 5):
* the application engine (``DATABASE_URL``) owns the schema and runs migrations;
* the audit engine (``AUDIT_DATABASE_URL``) connects as the ``audit_writer`` role,
  which may only INSERT/SELECT on ``audit_log``.
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import get_settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


@lru_cache
def get_engine() -> Engine:
    s = get_settings()
    return create_engine(
        s.database_url,
        pool_pre_ping=True,
        pool_size=s.db_pool_size,
        max_overflow=s.db_max_overflow,
        future=True,
    )


@lru_cache
def get_audit_engine() -> Engine:
    s = get_settings()
    return create_engine(s.audit_database_url, pool_pre_ping=True, pool_size=2, future=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
