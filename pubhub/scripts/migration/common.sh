#!/usr/bin/env bash

set -Eeuo pipefail

MIGRATION_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_PROJECT_DIR="$(cd "${MIGRATION_SCRIPT_DIR}/../.." && pwd)"
MIGRATION_COMPOSE_FILE="${MIGRATION_COMPOSE_FILE:-${MIGRATION_PROJECT_DIR}/docker-compose.prod.yml}"

if [[ ! -f "${MIGRATION_COMPOSE_FILE}" ]]; then
    echo "Compose file not found: ${MIGRATION_COMPOSE_FILE}" >&2
    exit 1
fi

compose() {
    local args=(-f "${MIGRATION_COMPOSE_FILE}")
    if [[ -n "${MIGRATION_COMPOSE_PROJECT:-}" ]]; then
        args=(-p "${MIGRATION_COMPOSE_PROJECT}" "${args[@]}")
    fi
    docker compose "${args[@]}" "$@"
}

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Required command not found: $1" >&2
        exit 1
    fi
}

postgres_exec() {
    compose exec -T postgres sh -c "$1"
}
