#!/bin/bash

# Fix CORS Configuration for Live Deployment
# This script applies the CORS fixes to resolve the live web frontend connection issue

set -e

echo "🔧 Fixing CORS Configuration for Live Deployment"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Backup current settings
echo "📋 Creating backup of current settings..."
cp backend/tanna_backend/settings.py backend/tanna_backend/settings.py.backup.$(date +%Y%m%d_%H%M%S)

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "⚠️  Warning: .env.prod file not found. Creating from template..."
    cp env.prod.template .env.prod
    echo "📝 Please edit .env.prod with your actual production values before continuing"
    echo "   Key variables to update:"
    echo "   - SECRET_KEY"
    echo "   - POSTGRES_PASSWORD"
    echo "   - FLW_CLIENT_ID, FLW_CLIENT_SECRET, FLUTTERWAVE_ENCRYPTION_KEY"
    echo "   - PGADMIN_PASSWORD"
    echo ""
    read -p "Press Enter after updating .env.prod to continue..."
fi

# Load environment variables
echo "🔍 Loading environment variables..."
if [ -f ".env.prod" ]; then
    export $(cat .env.prod | grep -v '^#' | xargs)
else
    echo "❌ Error: .env.prod file not found"
    exit 1
fi

# Verify required environment variables
echo "✅ Verifying environment configuration..."
required_vars=("SECRET_KEY" "POSTGRES_PASSWORD" "ALLOWED_HOSTS" "CORS_ALLOWED_ORIGINS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ Environment variables verified"

# Stop current services
echo "🛑 Stopping current services..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Build new images with updated configuration
echo "🔨 Building new images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
echo "🚀 Starting services with updated configuration..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
services=("backend" "frontend" "nginx")
for service in "${services[@]}"; do
    if docker-compose -f docker-compose.prod.yml ps | grep -q "$service.*Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running properly"
        docker-compose -f docker-compose.prod.yml logs "$service"
        exit 1
    fi
done

# Test API connectivity
echo "🧪 Testing API connectivity..."
if curl -f -s https://api.bottleplugug.com/api/health/ > /dev/null; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
    exit 1
fi

# Test CORS from main domain
echo "🌐 Testing CORS from main domain..."
if curl -f -s -H "Origin: https://bottleplugug.com" -H "Authorization: Bearer bottleplug-web-token-2024" https://api.bottleplugug.com/api/v1/products/categories/ > /dev/null; then
    echo "✅ CORS test passed"
else
    echo "❌ CORS test failed"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "================================================"
echo "✅ CORS configuration has been updated"
echo "✅ All services are running"
echo "✅ API connectivity verified"
echo "✅ CORS from main domain verified"
echo ""
echo "🌐 Your live website should now be able to connect to the backend:"
echo "   - Main site: https://bottleplugug.com"
echo "   - API: https://api.bottleplugug.com"
echo "   - Admin: https://admin.bottleplugug.com"
echo ""
echo "📊 To monitor the deployment:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🔄 To rollback if needed:"
echo "   cp backend/tanna_backend/settings.py.backup.* backend/tanna_backend/settings.py"
echo "   docker-compose -f docker-compose.prod.yml restart backend"
