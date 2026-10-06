#!/usr/bin/env bash
# First-time bring-up / update of the test stand. Idempotent.
#   PROJECT_DIR=/opt/kadrovik bash deploy/stand-up.sh
set -euo pipefail
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$PROJECT_DIR"

if [ ! -f .env ]; then
  echo "!! .env is missing: cp .env.example .env and set real secrets" >&2
  exit 1
fi

git pull --ff-only
docker compose build --pull
docker compose up -d --remove-orphans
docker compose ps
echo "== waiting for API"
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null; then
    curl -sS http://127.0.0.1:8000/health; echo
    exit 0
  fi
  sleep 2
done
echo "!! API did not become healthy" >&2
docker compose logs --tail=50 api >&2
exit 1
