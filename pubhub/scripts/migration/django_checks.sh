#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

echo "== Installed versions =="
compose run --rm django python -V
compose run --rm django python -m django --version
compose run --rm django python -c 'import psycopg; print(psycopg.__version__)'

echo "== Compatibility checks =="
compose run --rm django python -Wa manage.py check
compose run --rm django python manage.py makemigrations --check --dry-run
compose run --rm django python manage.py migrate --plan
compose run --rm django python manage.py test
