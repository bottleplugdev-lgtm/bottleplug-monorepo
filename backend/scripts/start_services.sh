#!/bin/bash

echo "Starting Tanna Backend Services..."

# Start Redis
echo "Starting Redis..."
redis-server --daemonize yes

# Start Django development server
echo "Starting Django server..."
python manage.py runserver &

# Start Celery worker
echo "Starting Celery worker..."
celery -A tanna_backend worker --loglevel=info &

# Start Celery beat (for periodic tasks)
echo "Starting Celery beat..."
celery -A tanna_backend beat --loglevel=info &

echo "All services started!"
echo "Django: http://localhost:8000"
echo "Redis: localhost:6379"
echo "Celery worker and beat are running in background"

# Keep script running
wait