#!/usr/bin/env bash

set -Eeuo pipefail

MIGRATION_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_PROJECT_DIR="$(cd "${MIGRATION_SCRIPT_DIR}/../.." && pwd)"
MIGRATION_COMPOSE_FILE="${MIGRATION_COMPOSE_FILE:-${MIGRATION_PROJECT_DIR}/docker-compose.prod.yml}"

if [[ ! -f "${MIGRATION_COMPOSE_FILE}" ]]; then
    echo "Compose file not found: ${MIGRATION_COMPOSE_FILE}" >&2
    exit 1
fi

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Required command not found: $1" >&2
        exit 1
    fi
}

detect_container_tooling() {
    local requested_engine="${MIGRATION_CONTAINER_ENGINE:-}"
    local docker_version=""

    if [[ -n "${requested_engine}" && "${requested_engine}" != "docker" && "${requested_engine}" != "podman" ]]; then
        echo "MIGRATION_CONTAINER_ENGINE must be 'docker' or 'podman'." >&2
        exit 1
    fi

    if [[ -z "${requested_engine}" && -n "${DOCKER_HOST:-}" && "${DOCKER_HOST}" == *podman* ]]; then
        requested_engine="podman"
    fi
    if [[ -z "${requested_engine}" && -n "${CONTAINER_HOST:-}" && "${CONTAINER_HOST}" == *podman* ]]; then
        requested_engine="podman"
    fi
    if [[ -z "${requested_engine}" ]] && command -v docker >/dev/null 2>&1; then
        docker_version="$(docker --version 2>/dev/null || true)"
        if [[ "${docker_version,,}" == *podman* ]] && command -v podman >/dev/null 2>&1; then
            requested_engine="podman"
        fi
    fi
    if [[ -z "${requested_engine}" ]] && command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        requested_engine="docker"
    fi
    if [[ -z "${requested_engine}" ]] && command -v podman >/dev/null 2>&1; then
        requested_engine="podman"
    fi

    case "${requested_engine}" in
        docker)
            require_command docker
            MIGRATION_ENGINE_COMMAND=(docker)
            if [[ -n "${MIGRATION_COMPOSE_PROVIDER:-}" && "${MIGRATION_COMPOSE_PROVIDER}" != "docker-compose" ]]; then
                echo "Docker requires MIGRATION_COMPOSE_PROVIDER=docker-compose when an override is supplied." >&2
                exit 1
            fi
            if ! docker compose version >/dev/null 2>&1; then
                echo "The Docker Compose plugin is required." >&2
                exit 1
            fi
            MIGRATION_COMPOSE_COMMAND=(docker compose)
            ;;
        podman)
            require_command podman
            MIGRATION_ENGINE_COMMAND=(podman)
            case "${MIGRATION_COMPOSE_PROVIDER:-auto}" in
                auto)
                    if command -v podman-compose >/dev/null 2>&1; then
                        MIGRATION_COMPOSE_COMMAND=(podman-compose)
                    elif podman compose version >/dev/null 2>&1; then
                        MIGRATION_COMPOSE_COMMAND=(podman compose)
                    else
                        echo "Podman requires podman-compose or 'podman compose'." >&2
                        exit 1
                    fi
                    ;;
                podman-compose)
                    require_command podman-compose
                    MIGRATION_COMPOSE_COMMAND=(podman-compose)
                    ;;
                podman)
                    if ! podman compose version >/dev/null 2>&1; then
                        echo "The 'podman compose' provider is unavailable." >&2
                        exit 1
                    fi
                    MIGRATION_COMPOSE_COMMAND=(podman compose)
                    ;;
                *)
                    echo "For Podman, MIGRATION_COMPOSE_PROVIDER must be 'podman-compose' or 'podman'." >&2
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "Neither Docker Compose nor Podman Compose could be detected." >&2
            exit 1
            ;;
    esac

    MIGRATION_CONTAINER_ENGINE="${requested_engine}"
    export MIGRATION_CONTAINER_ENGINE
}

detect_container_tooling

container_engine() {
    "${MIGRATION_ENGINE_COMMAND[@]}" "$@"
}

compose() {
    local args=(-f "${MIGRATION_COMPOSE_FILE}")
    if [[ -n "${MIGRATION_COMPOSE_PROJECT:-}" ]]; then
        args=(-p "${MIGRATION_COMPOSE_PROJECT}" "${args[@]}")
    fi
    "${MIGRATION_COMPOSE_COMMAND[@]}" "${args[@]}" "$@"
}

postgres_exec() {
    compose exec -T postgres sh -c "$1"
}

service_container_id() {
    local service="$1"
    local container_id

    container_id="$(compose ps -q "${service}" | head -n 1)"
    if [[ -z "${container_id}" ]]; then
        echo "No running container found for Compose service: ${service}" >&2
        return 1
    fi
    printf '%s\n' "${container_id}"
}

copy_from_service() {
    local service="$1"
    local source_path="$2"
    local destination_path="$3"
    local container_id

    container_id="$(service_container_id "${service}")"
    container_engine cp "${container_id}:${source_path}" "${destination_path}"
}

echo "Container tooling: ${MIGRATION_CONTAINER_ENGINE} (${MIGRATION_COMPOSE_COMMAND[*]})" >&2
