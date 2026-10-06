#!/usr/bin/env bash
# Runs once at cluster init (docker-entrypoint-initdb.d).
# Creates the LOGIN role used by the application's audit engine. Privileges on
# audit_log are granted by migration 0001 — this script only owns the password.
set -euo pipefail
: "${AUDIT_DB_PASSWORD:?AUDIT_DB_PASSWORD must be set}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'audit_writer') THEN
            CREATE ROLE audit_writer LOGIN PASSWORD '${AUDIT_DB_PASSWORD}';
        ELSE
            ALTER ROLE audit_writer LOGIN PASSWORD '${AUDIT_DB_PASSWORD}';
        END IF;
    END
    \$\$;
SQL
