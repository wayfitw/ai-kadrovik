#!/usr/bin/env bash
# Daily Postgres dump from the compose stack, rotated. Run from cron (see crontab.example).
#   PROJECT_DIR=/opt/kadrovik BACKUP_DIR=/var/backups/kadrovik KEEP_DAYS=14 bash deploy/backup-postgres.sh
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/kadrovik}"
KEEP_DAYS="${KEEP_DAYS:-14}"

cd "$PROJECT_DIR"
# shellcheck disable=SC1091
set -a; . ./.env; set +a

mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
OUT="$BACKUP_DIR/kadrovik-$STAMP.dump"

# Custom format: restore with `pg_restore -d kadrovik file.dump`.
docker compose exec -T postgres \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --compress=6 > "$OUT.tmp"
mv "$OUT.tmp" "$OUT"
sha256sum "$OUT" > "$OUT.sha256"

find "$BACKUP_DIR" -name 'kadrovik-*.dump*' -mtime "+$KEEP_DAYS" -delete
echo "backup written: $OUT ($(du -h "$OUT" | cut -f1))"
