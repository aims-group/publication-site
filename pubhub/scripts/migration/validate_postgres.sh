#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

EXPECTED_MAJOR="${1:-16}"

ACTUAL_MAJOR="$(postgres_exec 'psql -X -Aqt -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "show server_version_num;"' | tr -d '[:space:]')"
if [[ "${ACTUAL_MAJOR:0:2}" != "${EXPECTED_MAJOR}" ]]; then
    echo "Expected PostgreSQL major ${EXPECTED_MAJOR}, got server_version_num=${ACTUAL_MAJOR}" >&2
    exit 1
fi

echo "PostgreSQL major version: ${EXPECTED_MAJOR}"

INVALID_INDEXES="$(postgres_exec 'psql -X -Aqt -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select count(*) from pg_index where not indisvalid or not indisready;"' | tr -d '[:space:]')"
UNVALIDATED_CONSTRAINTS="$(postgres_exec 'psql -X -Aqt -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select count(*) from pg_constraint where not convalidated;"' | tr -d '[:space:]')"

echo "Invalid or unready indexes: ${INVALID_INDEXES}"
echo "Unvalidated constraints: ${UNVALIDATED_CONSTRAINTS}"

if [[ "${INVALID_INDEXES}" != "0" || "${UNVALIDATED_CONSTRAINTS}" != "0" ]]; then
    echo "Database validation failed." >&2
    exit 1
fi

postgres_exec 'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select schemaname, count(*) as tables from pg_tables where schemaname not in ('"'"'pg_catalog'"'"', '"'"'information_schema'"'"') group by schemaname order by schemaname;"'
postgres_exec 'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select extname, extversion from pg_extension order by extname;"'

echo "PostgreSQL structural validation passed. Compare business row counts separately."
