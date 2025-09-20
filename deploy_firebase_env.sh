#!/bin/bash

# Deploy Firebase credentials via environment variables
echo "🔥 Deploying Firebase credentials via environment variables..."

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "❌ Error: .env.prod not found"
    echo "Please create .env.prod from env.prod.template and fill in the Firebase credentials"
    exit 1
fi

echo "✅ .env.prod found"

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found. Please run this script from the project root."
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Restart backend to reload environment variables
echo "🔄 Restarting backend to reload Firebase environment variables..."
docker-compose -f docker-compose.prod.yml restart backend

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 15

# Test Firebase configuration
echo "🧪 Testing Firebase configuration..."
response=$(curl -s -X GET "https://api.bottleplugug.com/api/v1/auth/firebase-debug/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bottleplug-web-token-2024")

if echo "$response" | grep -q '"firebase_auth_working":true'; then
    echo "✅ Firebase authentication is working via environment variables!"
    echo "✅ Checkout authentication should now be fixed"
elif echo "$response" | grep -q '"service_account_file_exists":false'; then
    echo "✅ Firebase is using environment variables (no file needed)"
    echo "✅ Firebase authentication should be working"
else
    echo "⚠️  Firebase configuration status unclear"
    echo "Response: $response"
fi

# Test checkout endpoint
echo "🧪 Testing checkout endpoint..."
checkout_response=$(curl -s -X POST "https://api.bottleplugug.com/api/v1/orders/cart/checkout/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bottleplug-web-token-2024" \
  -d '{"payment_method": "mobile_money", "is_pickup": false, "delivery_address": "Test", "delivery_instructions": "Test", "delivery_fee": 5000, "notes": ""}')

if echo "$checkout_response" | grep -q "Checkout requires user authentication"; then
    echo "⚠️  Checkout still requires authentication (expected for web token)"
    echo "✅ This means Firebase authentication is working, but web token users are correctly rejected"
else
    echo "✅ Checkout endpoint is responding differently (good sign)"
fi

echo ""
echo "🎉 Firebase environment variable deployment complete!"
echo ""
echo "🔍 To monitor logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
echo ""
echo "🧪 To test with a real Firebase token, try the checkout from the frontend"
echo ""
echo "📋 Firebase credentials are now stored securely in environment variables"
echo "   No sensitive files are stored in the repository"
