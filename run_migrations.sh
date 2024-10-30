#!/bin/bash
set -e  # Exit on error

# Logging helper
log() { echo "$(date +"%Y-%m-%d %T") - $1"; }

# Wait for the database to be ready
log "Waiting for the database to be ready..."
until pg_isready -h "$DB_HOST" -U "$DB_USERNAME" -d "$DB_DATABASE"; do
  log "Database is not ready yet. Retrying in 5 seconds..."
  sleep 5
done

log "Database is ready. Checking and applying migrations if needed..."

# Define the lock file
LOCK_FILE="/tmp/alembic_migration.lock"

# Check if the lock file exists and create it safely
if [ -e "$LOCK_FILE" ]; then
  log "Migration already in progress. Exiting."
  exit 1
else
  touch "$LOCK_FILE"
fi

# Ensure the lock file is removed after the script ends
trap 'rm -f "$LOCK_FILE"' EXIT

# Check if the latest migration has been applied
LATEST_MIGRATION=$(alembic heads | awk '{print $1}')
CURRENT_MIGRATION=$(alembic current | awk '{print $1}')

if [ "$LATEST_MIGRATION" = "$CURRENT_MIGRATION" ]; then
  log "Database is at the latest migration. Checking for schema changes..."

  # Attempt to create a migration only if there are schema changes
  alembic revision --autogenerate -m "Auto migration"
  MIGRATION_FILE=$(ls -Art alembic/versions | tail -n 1)

  # If the new migration file is empty, delete it
  if grep -q 'pass' "alembic/versions/$MIGRATION_FILE"; then
    log "No schema changes detected; deleting empty migration."
    rm "alembic/versions/$MIGRATION_FILE"
  else
    log "Schema changes detected; applying migration."
  fi
else
  log "Pending migrations detected, applying..."
fi

# Apply all migrations
alembic upgrade head
log "Migrations applied successfully."

# Remove the lock file explicitly to avoid persistence issues
rm -f "$LOCK_FILE"

# Run the main application
exec "$@"
