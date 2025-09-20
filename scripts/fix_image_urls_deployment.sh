#!/bin/bash

# Fix Image URLs for Live Frontend
# This script deploys the image URL fixes to resolve broken images on live website

set -e

echo "🖼️  Fixing Image URLs for Live Frontend"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "⚠️  Warning: .env.prod file not found. Creating from template..."
    cp env.prod.template .env.prod
    echo "📝 Please edit .env.prod with your actual production values before continuing"
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

# Stop current services
echo "🛑 Stopping current services..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Build new frontend image with updated image URL fixes
echo "🔨 Building new frontend image with image URL fixes..."
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# Start services
echo "🚀 Starting services with updated image URL configuration..."
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

# Test image URLs
echo "🖼️  Testing image URLs..."
if curl -f -s https://api.bottleplugug.com/media/categories/red_wine.jpeg > /dev/null; then
    echo "✅ Backend media serving works"
else
    echo "❌ Backend media serving failed"
    exit 1
fi

if curl -f -s https://bottleplugug.com/media/categories/red_wine.jpeg > /dev/null; then
    echo "✅ Nginx media proxy works"
else
    echo "❌ Nginx media proxy failed"
    exit 1
fi

echo ""
echo "🎉 Image URL fixes deployed successfully!"
echo "======================================"
echo "✅ Hardcoded localhost URLs replaced with production URLs"
echo "✅ All Vue components now use centralized image utilities"
echo "✅ Frontend rebuilt with updated image configuration"
echo "✅ All services are running"
echo "✅ Media serving verified"
echo ""
echo "🌐 Your live website should now display images correctly:"
echo "   - Products page: https://bottleplugug.com/products"
echo "   - Wishlist page: https://bottleplugug.com/wishlist"
echo "   - All other pages with product/event images"
echo ""
echo "📊 To monitor the deployment:"
echo "   docker-compose -f docker-compose.prod.yml logs -f frontend"
echo ""
echo "🔄 To rollback if needed:"
echo "   git checkout HEAD~1 -- web/src/views/"
echo "   docker-compose -f docker-compose.prod.yml build --no-cache frontend"
echo "   docker-compose -f docker-compose.prod.yml up -d"
