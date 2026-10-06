#!/usr/bin/env bash
# Dev/stand only: a separate database for `make test` so that the test fixtures
# (alembic downgrade base → upgrade head) never touch the working data.
set -euo pipefail
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
    SELECT 'CREATE DATABASE ${POSTGRES_DB}_test OWNER ${POSTGRES_USER}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}_test')\gexec
SQL
