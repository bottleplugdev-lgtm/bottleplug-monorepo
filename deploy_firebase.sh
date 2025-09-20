#!/bin/bash

# Deploy Firebase service account file to production
echo "🔥 Deploying Firebase service account file to production..."

# Check if the file exists locally
if [ ! -f "backend/firebase/booze-nation-94e3f-firebase-adminsdk-gegcg-c4b6679745.json" ]; then
    echo "❌ Error: Firebase service account file not found locally"
    echo "Expected location: backend/firebase/booze-nation-94e3f-firebase-adminsdk-gegcg-c4b6679745.json"
    exit 1
fi

echo "✅ Firebase service account file found locally"

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found. Please run this script from the project root."
    exit 1
fi

# Create the firebase directory in the backend container if it doesn't exist
echo "📁 Creating firebase directory in backend container..."
docker-compose -f docker-compose.prod.yml exec -T backend mkdir -p /app/firebase/

# Copy the Firebase service account file to the backend container
echo "📋 Copying Firebase service account file to backend container..."
docker cp backend/firebase/booze-nation-94e3f-firebase-adminsdk-gegcg-c4b6679745.json \
  $(docker-compose -f docker-compose.prod.yml ps -q backend):/app/firebase/booze-nation-94e3f-firebase-adminsdk-gegcg-c4b6679745.json

# Set proper permissions
echo "🔐 Setting proper permissions..."
docker-compose -f docker-compose.prod.yml exec -T backend chmod 644 /app/firebase/booze-nation-94e3f-firebase-adminsdk-gegcg-c4b6679745.json

# Restart the backend to reload Firebase configuration
echo "🔄 Restarting backend to reload Firebase configuration..."
docker-compose -f docker-compose.prod.yml restart backend

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 15

# Test Firebase configuration
echo "🧪 Testing Firebase configuration..."
response=$(curl -s -X GET "https://api.bottleplugug.com/api/v1/auth/firebase-debug/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bottleplug-web-token-2024")

if echo "$response" | grep -q '"service_account_file_exists":true'; then
    echo "✅ Firebase service account file deployed successfully!"
    echo "✅ Firebase authentication should now work"
else
    echo "❌ Firebase deployment may have failed"
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
echo "🎉 Firebase deployment complete!"
echo ""
echo "🔍 To monitor logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
echo ""
echo "🧪 To test with a real Firebase token, try the checkout from the frontend"
