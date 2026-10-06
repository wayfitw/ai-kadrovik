#!/usr/bin/env bash
# Restore a dump produced by backup-postgres.sh into the compose stack (drops objects first).
#   bash deploy/restore-postgres.sh /var/backups/kadrovik/kadrovik-20261006-020000.dump
set -euo pipefail
DUMP="${1:?path to .dump}"
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$PROJECT_DIR"
# shellcheck disable=SC1091
set -a; . ./.env; set +a
sha256sum -c "$DUMP.sha256"
docker compose exec -T postgres \
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner < "$DUMP"
echo "restored from $DUMP"
