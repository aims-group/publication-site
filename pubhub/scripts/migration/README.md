# Migration helper scripts

These scripts implement guarded parts of `PRODUCTION_MIGRATION_PLAN.md`. Run them from any directory. They default to `docker-compose.prod.yml`; override that with `MIGRATION_COMPOSE_FILE`. Set `MIGRATION_COMPOSE_PROJECT` when production uses a non-default Compose project name.

```bash
# Read-only inventory of running production services
./scripts/migration/preflight.sh

# Final backup after every database writer has been stopped
MIGRATION_WRITES_STOPPED=yes ./scripts/migration/backup_postgres.sh /approved/backup/path

# Validate the restored PostgreSQL 16 service
./scripts/migration/validate_postgres.sh 16

# Run Django compatibility checks and tests in one-off containers
./scripts/migration/django_checks.sh

# Rehearse a 12.6 to 16.3 restore in isolated, automatically cleaned resources
./scripts/migration/rehearse_postgres_upgrade.sh backups/backup.sql.gz

# Include Django checks and tests against the migrated PostgreSQL 16 database
MIGRATION_DJANGO_IMAGE=pubhub_local_django:latest \
  ./scripts/migration/rehearse_postgres_upgrade.sh backups/backup.sql.gz

# Exercise the production image and production settings
MIGRATION_DJANGO_IMAGE=pubhub_production_django:latest \
MIGRATION_DJANGO_SETTINGS=config.settings.production \
  ./scripts/migration/rehearse_postgres_upgrade.sh backups/backup.sql.gz
```

The rehearsal script accepts a gzip-compressed plain SQL dump or a custom-format dump. It restores the backup to PostgreSQL 12.6, creates a fresh custom dump, restores that dump to PostgreSQL 16.3, compares exact counts for every user table, and checks indexes and constraints. Set `MIGRATION_DJANGO_IMAGE` to additionally run Django's system, model-drift, migration, and test-suite checks against the migrated database. Its containers, network, volumes, and temporary files have a unique `pubhub_migration_test_` prefix and are removed on exit.

The backup script intentionally does not stop services itself because this repository may not contain every production writer. It requires an explicit `MIGRATION_WRITES_STOPPED=yes` acknowledgement.
