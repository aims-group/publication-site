#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

if [[ "${MIGRATION_WRITES_STOPPED:-}" != "yes" ]]; then
    echo "Refusing final migration backup because writes are not confirmed stopped." >&2
    echo "Stop every writer, then run with MIGRATION_WRITES_STOPPED=yes." >&2
    exit 2
fi

require_command docker

OUTPUT_DIR="${1:-${MIGRATION_PROJECT_DIR}/migration-backups}"
mkdir -p "${OUTPUT_DIR}"
OUTPUT_DIR="$(cd "${OUTPUT_DIR}" && pwd)"
STAMP="$(date -u +'%Y_%m_%dT%H_%M_%SZ')"
DATABASE_DUMP="pre_pg16_${STAMP}.dump"
GLOBALS_DUMP="pre_pg16_globals_${STAMP}.sql"

echo "Creating a consistent custom-format database dump..."
postgres_exec 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl --file=/backups/'"${DATABASE_DUMP}"
postgres_exec 'pg_dumpall -U "$POSTGRES_USER" --globals-only --file=/backups/'"${GLOBALS_DUMP}"
postgres_exec 'pg_restore --list /backups/'"${DATABASE_DUMP}"' >/dev/null'

compose cp "postgres:/backups/${DATABASE_DUMP}" "${OUTPUT_DIR}/${DATABASE_DUMP}"
compose cp "postgres:/backups/${GLOBALS_DUMP}" "${OUTPUT_DIR}/${GLOBALS_DUMP}"

if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "${OUTPUT_DIR}/${DATABASE_DUMP}" "${OUTPUT_DIR}/${GLOBALS_DUMP}" > "${OUTPUT_DIR}/SHA256SUMS_${STAMP}"
else
    shasum -a 256 "${OUTPUT_DIR}/${DATABASE_DUMP}" "${OUTPUT_DIR}/${GLOBALS_DUMP}" > "${OUTPUT_DIR}/SHA256SUMS_${STAMP}"
fi

echo "Backup complete: ${OUTPUT_DIR}/${DATABASE_DUMP}"
echo "Copy the dump and checksum to approved off-host storage before cutover."
