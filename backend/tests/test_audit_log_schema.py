"""Block 1.1: the first migration applies and audit_log is append-only at DB level.

The hash-chained writer itself is block 2.1; here we only prove the schema guards:
* role ``audit_writer`` can INSERT and SELECT, nothing else;
* UPDATE / DELETE / TRUNCATE are rejected for every role, including the owner.
"""

import pytest
from sqlalchemy import create_engine, text

from tests.conftest import requires_db

pytestmark = requires_db


@pytest.fixture
def engine(migrated_db: str):
    eng = create_engine(migrated_db, future=True)
    # The migration creates the role NOLOGIN; to exercise its grants we become a member
    # of it. This works for a superuser (CI) and for the role's creator (ADMIN OPTION).
    with eng.begin() as conn:
        conn.execute(text("GRANT audit_writer TO CURRENT_USER"))
    yield eng
    eng.dispose()


def _insert(conn, note: str) -> int:
    return conn.execute(
        text(
            "INSERT INTO audit_log (actor_kind, action, hash, note) "
            "VALUES ('system', 'test', :h, :n) RETURNING id"
        ),
        {"h": "0" * 64, "n": note},
    ).scalar_one()


def test_migration_creates_table_and_role(engine) -> None:
    with engine.connect() as conn:
        assert conn.execute(text("SELECT to_regclass('public.audit_log')")).scalar_one()
        assert conn.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = 'audit_writer'")
        ).scalar_one()
        privs = conn.execute(
            text(
                "SELECT privilege_type FROM information_schema.role_table_grants "
                "WHERE grantee = 'audit_writer' AND table_name = 'audit_log'"
            )
        ).scalars()
        assert set(privs) == {"INSERT", "SELECT"}


@pytest.mark.parametrize(
    "stmt",
    [
        "UPDATE audit_log SET note = 'changed' WHERE id = :id",
        "DELETE FROM audit_log WHERE id = :id",
        "TRUNCATE audit_log",
    ],
)
def test_owner_cannot_mutate(engine, stmt: str) -> None:
    with engine.begin() as conn:
        row_id = _insert(conn, "owner-row")
    with engine.connect() as conn:
        with pytest.raises(Exception, match="append-only|permission denied"):
            conn.execute(text(stmt), {"id": row_id})
        conn.rollback()
        assert (
            conn.execute(
                text("SELECT note FROM audit_log WHERE id = :id"), {"id": row_id}
            ).scalar_one()
            == "owner-row"
        )


def test_audit_writer_can_only_insert(engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("SET ROLE audit_writer"))
        row_id = _insert(conn, "writer-row")
        assert conn.execute(text("SELECT count(*) FROM audit_log")).scalar_one() >= 1
        conn.commit()

    for stmt in (
        "UPDATE audit_log SET note = 'x' WHERE id = :id",
        "DELETE FROM audit_log WHERE id = :id",
    ):
        with engine.connect() as conn:
            conn.execute(text("SET ROLE audit_writer"))
            with pytest.raises(Exception, match="append-only|permission denied"):
                conn.execute(text(stmt), {"id": row_id})
            conn.rollback()
