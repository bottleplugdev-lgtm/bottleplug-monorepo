#!/bin/bash
set -e

# Wait for database
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

# Skip migrations for now to test basic setup
echo "Skipping migrations temporarily..."
# python manage.py migrate

# Skip superuser creation for now
echo "Skipping superuser creation temporarily..."

echo "Bottleplug backend setup complete!"

# Start server
exec "$@"
