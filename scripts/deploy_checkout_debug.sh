#!/bin/bash

# Deploy checkout debugging changes to production
# This script applies the Firebase authentication debugging changes

set -e

echo "🚀 Deploying checkout debugging changes to production..."

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found. Please run this script from the project root."
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes from git..."
git pull origin main

# Check if there are any uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: There are uncommitted changes. Please commit or stash them first."
    git status --short
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled."
        exit 1
    fi
fi

# Restart backend to apply debugging changes
echo "🔄 Restarting backend service..."
docker-compose -f docker-compose.prod.yml restart backend

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

# Check backend health
echo "🏥 Checking backend health..."
if curl -s "https://api.bottleplugug.com/api/health/" | grep -q "ok"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo "📋 Backend logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20 backend
    exit 1
fi

# Show recent backend logs
echo "📋 Recent backend logs (last 20 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=20 backend

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔍 To monitor logs in real-time, run:"
echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
echo ""
echo "🧪 To test checkout, try making a request and check the logs for:"
echo "   - 'Firebase authentication successful for user: [email] (type: customer)'"
echo "   - 'Checkout request from user: [user] (type: customer, authenticated: True)'"
echo "   - 'Firebase authentication failed: [error message]' (if there are issues)"
