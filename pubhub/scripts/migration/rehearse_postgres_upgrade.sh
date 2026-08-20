#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 SOURCE_BACKUP.sql.gz|SOURCE_BACKUP.dump" >&2
    exit 2
fi

SOURCE_BACKUP="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
if [[ ! -f "${SOURCE_BACKUP}" ]]; then
    echo "Backup not found: ${SOURCE_BACKUP}" >&2
    exit 1
fi

for command_name in diff sort mktemp; do
    require_command "${command_name}"
done

RUN_ID="$$"
RESOURCE_PREFIX="pubhub_migration_test_${RUN_ID}"
PG12_CONTAINER="${RESOURCE_PREFIX}_pg12"
PG16_CONTAINER="${RESOURCE_PREFIX}_pg16"
PG12_VOLUME="${RESOURCE_PREFIX}_pg12_data"
PG16_VOLUME="${RESOURCE_PREFIX}_pg16_data"
NETWORK="${RESOURCE_PREFIX}_network"
TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pubhub-migration.XXXXXX")"
PASSWORD="migration-test-only"

cleanup() {
    if [[ "${RESOURCE_PREFIX}" != pubhub_migration_test_* ]]; then
        echo "Unexpected resource prefix; refusing cleanup: ${RESOURCE_PREFIX}" >&2
        return
    fi
    container_engine rm -f "${PG12_CONTAINER}" "${PG16_CONTAINER}" >/dev/null 2>&1 || true
    container_engine network rm "${NETWORK}" >/dev/null 2>&1 || true
    container_engine volume rm "${PG12_VOLUME}" "${PG16_VOLUME}" >/dev/null 2>&1 || true
    if [[ "${TEMP_DIR}" == "${TMPDIR:-/tmp}"/pubhub-migration.* ]]; then
        rm -rf "${TEMP_DIR}"
    else
        echo "Unexpected temporary path; refusing cleanup: ${TEMP_DIR}" >&2
    fi
}
trap cleanup EXIT

wait_for_postgres() {
    local container="$1"
    local attempts=60
    until container_engine exec "${container}" pg_isready -U postgres -d pubhub >/dev/null 2>&1; do
        attempts=$((attempts - 1))
        if [[ ${attempts} -eq 0 ]]; then
            echo "PostgreSQL did not become ready: ${container}" >&2
            return 1
        fi
        sleep 1
    done
}

capture_counts() {
    local container="$1"
    local output="$2"
    container_engine exec -i "${container}" psql -X -Aqt -v ON_ERROR_STOP=1 -U postgres -d pubhub > "${output}" <<'SQL'
SELECT format(
    'SELECT %L || E''\t'' || count(*) FROM %I.%I;',
    schemaname || '.' || tablename,
    schemaname,
    tablename
)
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;
\gexec
SQL
    sort -o "${output}" "${output}"
}

echo "Creating isolated PostgreSQL 12 and 16 resources with prefix ${RESOURCE_PREFIX}..."
container_engine network create "${NETWORK}" >/dev/null
container_engine volume create "${PG12_VOLUME}" >/dev/null
container_engine volume create "${PG16_VOLUME}" >/dev/null

container_engine run -d --name "${PG12_CONTAINER}" --network "${NETWORK}" \
    -e POSTGRES_PASSWORD="${PASSWORD}" -e POSTGRES_DB=pubhub \
    -v "${PG12_VOLUME}:/var/lib/postgresql/data" docker.io/library/postgres:12.6 >/dev/null
wait_for_postgres "${PG12_CONTAINER}"

echo "Restoring the source backup into PostgreSQL 12..."
case "${SOURCE_BACKUP}" in
    *.sql.gz)
        gzip -dc "${SOURCE_BACKUP}" | container_engine exec -i "${PG12_CONTAINER}" psql -X -q -v ON_ERROR_STOP=1 -U postgres -d pubhub >/dev/null
        ;;
    *.dump)
        container_engine cp "${SOURCE_BACKUP}" "${PG12_CONTAINER}:/tmp/source.dump"
        container_engine exec "${PG12_CONTAINER}" pg_restore --exit-on-error -U postgres -d pubhub /tmp/source.dump
        ;;
    *)
        echo "Unsupported backup type: ${SOURCE_BACKUP}" >&2
        exit 2
        ;;
esac

capture_counts "${PG12_CONTAINER}" "${TEMP_DIR}/pg12-counts.tsv"
container_engine exec "${PG12_CONTAINER}" pg_dump -U postgres -d pubhub --format=custom --no-owner --no-acl --file=/tmp/pg12.dump
container_engine cp "${PG12_CONTAINER}:/tmp/pg12.dump" "${TEMP_DIR}/pg12.dump" >/dev/null

container_engine run -d --name "${PG16_CONTAINER}" --network "${NETWORK}" \
    -e POSTGRES_PASSWORD="${PASSWORD}" -e POSTGRES_DB=pubhub \
    -v "${PG16_VOLUME}:/var/lib/postgresql/data" docker.io/library/postgres:16.3 >/dev/null
wait_for_postgres "${PG16_CONTAINER}"

echo "Restoring the PostgreSQL 12 dump into PostgreSQL 16..."
container_engine cp "${TEMP_DIR}/pg12.dump" "${PG16_CONTAINER}:/tmp/pg12.dump"
container_engine exec "${PG16_CONTAINER}" pg_restore --exit-on-error -U postgres -d pubhub --no-owner --no-acl /tmp/pg12.dump
container_engine exec "${PG16_CONTAINER}" vacuumdb -U postgres -d pubhub --analyze-in-stages >/dev/null
capture_counts "${PG16_CONTAINER}" "${TEMP_DIR}/pg16-counts.tsv"

diff -u "${TEMP_DIR}/pg12-counts.tsv" "${TEMP_DIR}/pg16-counts.tsv"

INVALID_INDEXES="$(container_engine exec "${PG16_CONTAINER}" psql -X -Aqt -U postgres -d pubhub -c 'select count(*) from pg_index where not indisvalid or not indisready;')"
UNVALIDATED_CONSTRAINTS="$(container_engine exec "${PG16_CONTAINER}" psql -X -Aqt -U postgres -d pubhub -c 'select count(*) from pg_constraint where not convalidated;')"
if [[ "${INVALID_INDEXES}" != "0" || "${UNVALIDATED_CONSTRAINTS}" != "0" ]]; then
    echo "Target validation failed: invalid indexes=${INVALID_INDEXES}, unvalidated constraints=${UNVALIDATED_CONSTRAINTS}" >&2
    exit 1
fi

if [[ -n "${MIGRATION_DJANGO_IMAGE:-}" ]]; then
    if ! container_engine image inspect "${MIGRATION_DJANGO_IMAGE}" >/dev/null 2>&1; then
        echo "Django image not found: ${MIGRATION_DJANGO_IMAGE}" >&2
        exit 1
    fi

    DJANGO_SETTINGS="${MIGRATION_DJANGO_SETTINGS:-config.settings.local}"

    django_manage() {
        container_engine run --rm --network "${NETWORK}" \
            -e DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS}" \
            -e DJANGO_ALLOWED_HOSTS=localhost \
            -e DJANGO_SECRET_KEY=migration-test-only-secret-key-with-more-than-fifty-characters \
            -e DJANGO_LOGGING_FILENAME=/tmp/publications-site.log \
            -e POSTGRES_DB=pubhub \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_PASSWORD="${PASSWORD}" \
            -e POSTGRES_HOST="${PG16_CONTAINER}" \
            -e POSTGRES_PORT=5432 \
            "${MIGRATION_DJANGO_IMAGE}" python manage.py "$@"
    }

    echo "Running Django checks against the migrated PostgreSQL 16 database..."
    django_manage check
    if [[ "${DJANGO_SETTINGS}" == "config.settings.production" ]]; then
        django_manage check --deploy
        django_manage collectstatic --noinput
    fi
    django_manage makemigrations --check --dry-run
    django_manage migrate --check
    django_manage test
fi

echo "Migration rehearsal passed: all table row counts match and PostgreSQL 16 structures are valid."
