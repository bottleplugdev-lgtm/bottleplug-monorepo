#!/bin/bash

# Quick deployment script for the Firebase authentication fix
echo "🚀 Deploying Firebase authentication fix..."

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Restart backend
echo "🔄 Restarting backend..."
docker-compose -f docker-compose.prod.yml restart backend

# Wait for restart
echo "⏳ Waiting for backend to restart..."
sleep 15

# Test the fix
echo "🧪 Testing the fix..."
response=$(curl -s -X POST "https://api.bottleplugug.com/api/v1/orders/cart/checkout/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bottleplug-web-token-2024" \
  -d '{"payment_method": "mobile_money", "is_pickup": false, "delivery_address": "Test", "delivery_instructions": "Test", "delivery_fee": 5000, "notes": ""}')

if echo "$response" | grep -q "Checkout requires user authentication"; then
    echo "❌ Fix not applied yet - still getting authentication error"
    echo "📋 Backend logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=10 backend
else
    echo "✅ Fix appears to be working!"
    echo "Response: $response"
fi

echo ""
echo "🔍 To monitor logs in real-time:"
echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
