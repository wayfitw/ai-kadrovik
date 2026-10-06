"""audit_log table and audit_writer role (append-only at DB level)

Revision ID: 0001
Revises:
Create Date: 2026-10-06

CLAUDE.md, principle 5: ``audit_log`` has no UPDATE/DELETE at the DB-rights level.
Two independent guards are installed:

1. role ``audit_writer`` gets INSERT + SELECT only (UPDATE/DELETE/TRUNCATE revoked,
   also from PUBLIC);
2. a trigger rejects UPDATE/DELETE/TRUNCATE for *every* role, including the owner,
   so the table is immutable even through the application engine.

The role is created NOLOGIN if it does not exist yet; the LOGIN password is set by
the deployment (docker/postgres/initdb/01-audit-writer.sh), never by a migration.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AUDIT_ROLE = "audit_writer"


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
        sa.Column("actor_kind", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=True),
        sa.Column("rule_version_id", sa.BigInteger(), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("payload_ref", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("prev_hash", sa.String(length=64), nullable=True),
        sa.Column("hash", sa.String(length=64), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
    )
    op.create_index("ix_audit_log_org_ts", "audit_log", ["organization_id", "ts"])

    # --- guard 1: role with INSERT/SELECT only -------------------------------
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{AUDIT_ROLE}') THEN
                CREATE ROLE {AUDIT_ROLE} NOLOGIN;
            END IF;
        END
        $$;
        """
    )
    op.execute(f"GRANT USAGE ON SCHEMA public TO {AUDIT_ROLE}")
    op.execute(f"GRANT SELECT, INSERT ON TABLE audit_log TO {AUDIT_ROLE}")
    op.execute(f"GRANT USAGE, SELECT ON SEQUENCE audit_log_id_seq TO {AUDIT_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE, TRUNCATE ON TABLE audit_log FROM {AUDIT_ROLE}")
    op.execute("REVOKE UPDATE, DELETE, TRUNCATE ON TABLE audit_log FROM PUBLIC")

    # --- guard 2: trigger that rejects mutation for everyone -----------------
    op.execute(
        """
        CREATE OR REPLACE FUNCTION audit_log_forbid_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only: % is not allowed', TG_OP
                USING ERRCODE = 'insufficient_privilege';
        END
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_log_immutable_row
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW EXECUTE FUNCTION audit_log_forbid_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_log_immutable_truncate
        BEFORE TRUNCATE ON audit_log
        FOR EACH STATEMENT EXECUTE FUNCTION audit_log_forbid_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_log_immutable_truncate ON audit_log")
    op.execute("DROP TRIGGER IF EXISTS audit_log_immutable_row ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS audit_log_forbid_mutation()")
    op.execute(f"REVOKE ALL ON TABLE audit_log FROM {AUDIT_ROLE}")
    op.execute(f"REVOKE ALL ON SEQUENCE audit_log_id_seq FROM {AUDIT_ROLE}")
    op.drop_index("ix_audit_log_org_ts", table_name="audit_log")
    op.drop_table("audit_log")
    # The role is shared infrastructure and is intentionally not dropped.
