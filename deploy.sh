#!/bin/bash

# Quick deployment script for BottlePlug
# Run this script to deploy updates to production

set -e

echo "🚀 Deploying BottlePlug to production..."

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found. Are you in the right directory?"
    exit 1
fi

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "❌ Error: .env.prod not found. Please create it from env.prod.template"
    exit 1
fi

# Create backup
echo "💾 Creating backup..."
if [ -d "backup" ]; then
    rm -rf backup/old_*
    mv backup backup/old_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
fi

# Stop current containers
echo "🛑 Stopping current containers..."
docker-compose -f docker-compose.prod.yml down

# Pull latest changes (if using git)
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes..."
    git pull origin main
fi

# Build and start new containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# Restart services to ensure everything is working
echo "🔄 Restarting services..."
docker-compose -f docker-compose.prod.yml restart

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f

# Check if everything is running
echo "✅ Checking deployment status..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "🎉 Deployment completed successfully!"
    echo "🌐 Your application should be available at: https://yourdomain.com"
else
    echo "❌ Some containers are not running. Check logs:"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

echo ""
echo "📊 Useful commands:"
echo "- View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "- Check status: docker-compose -f docker-compose.prod.yml ps"
echo "- Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "- Access database: docker-compose -f docker-compose.prod.yml exec db psql -U bottleplug -d bottleplug_prod"
