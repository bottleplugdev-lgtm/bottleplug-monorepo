#!/bin/bash

# Script to start Celery worker and beat scheduler for payment status checking

echo "Starting Celery services for payment status checking..."

# Start Celery worker
echo "Starting Celery worker..."
celery -A tanna_backend worker --loglevel=info &

# Start Celery beat scheduler
echo "Starting Celery beat scheduler..."
celery -A tanna_backend beat --loglevel=info &

echo "Celery services started successfully!"
echo "Payment status checking will run every 5 minutes"
echo "Webhook cleanup will run every 24 hours"
echo ""
echo "To stop the services, use: pkill -f celery" 