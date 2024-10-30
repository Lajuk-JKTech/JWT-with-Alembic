#!/bin/bash
set -e  # Exit on error

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
until pg_isready -h "$DB_HOST" -U "$DB_USERNAME" -d "$DB_DATABASE"; do
  echo "Database is not ready yet. Retrying in 5 seconds..."
  sleep 5
done

echo "Database is ready. Generating and applying migrations..."

# Generate a new migration (if there are schema changes)
alembic revision --autogenerate -m "Auto migration" || echo "No changes detected."

# Apply migrations
alembic upgrade head

# Execute the main CMD from the Dockerfile (uvicorn server start)
exec "$@"
