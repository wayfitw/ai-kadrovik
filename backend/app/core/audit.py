"""ORM model of the append-only audit log.

Schema only (block 1.1). The hash-chained writer, the ``audit_writer`` connection
and the "UPDATE is rejected" tests belong to block 2.1.
Rows never store personal data — only identifiers and payload references.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_log_org_ts", "organization_id", "ts"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    organization_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    actor_kind: Mapped[str] = mapped_column(String(32), nullable=False)  # user | system | worker
    actor_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rule_version_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_ref: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    prev_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hash: Mapped[str] = mapped_column(String(64), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
