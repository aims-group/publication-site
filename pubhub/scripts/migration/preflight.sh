#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

require_command docker

echo "== Compose services =="
compose config --services

echo "== Container images =="
compose images

echo "== PostgreSQL =="
postgres_exec 'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select version();"'
postgres_exec 'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select current_database() as database, current_user as owner, pg_size_pretty(pg_database_size(current_database())) as size;"'
postgres_exec 'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select extname, extversion from pg_extension order by extname;"'

echo "== Django and Python =="
compose exec -T django python -V
compose exec -T django python -m django --version
compose exec -T django python -c 'import psycopg; print(psycopg.__version__)'

echo "== Django checks =="
compose exec -T django python manage.py check
compose exec -T django python manage.py showmigrations --plan
