#!/bin/bash

# Production Flutterwave Configuration Fix Script
# This script ensures the correct Flutterwave v4 API configuration is always applied
# Run this script after any deployment to guarantee correct settings

set -e

echo "🔧 Fixing Flutterwave Production Configuration..."

# Define the correct production configuration (Official Flutterwave v4 URLs)
PRODUCTION_BASE_URL="https://f4bexperience.flutterwave.com"
OAUTH_TOKEN_URL="https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token"

# Check if we're in the correct directory
if [ ! -f ".env.prod" ]; then
    echo "❌ Error: .env.prod file not found. Make sure you're in the /opt/bottleplug directory"
    exit 1
fi

echo "📋 Current Flutterwave configuration:"
grep -E "FLUTTERWAVE|FLW_" .env.prod | head -10

# Create backup of current .env.prod
BACKUP_FILE=".env.prod.backup.$(date +%Y%m%d_%H%M%S)"
cp .env.prod "$BACKUP_FILE"
echo "💾 Backup created: $BACKUP_FILE"

# Function to update or add environment variable
update_env_var() {
    local key="$1"
    local value="$2"
    local file="$3"
    
    if grep -q "^${key}=" "$file"; then
        # Update existing variable
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
        echo "✅ Updated: $key"
    else
        # Add new variable
        echo "${key}=${value}" >> "$file"
        echo "✅ Added: $key"
    fi
}

# Apply the correct Flutterwave v4 production configuration
echo "🔧 Applying correct Flutterwave v4 configuration..."

update_env_var "FLUTTERWAVE_ENVIRONMENT" "production" ".env.prod"
update_env_var "FLUTTERWAVE_BASE_URL" "$PRODUCTION_BASE_URL" ".env.prod"
update_env_var "FLUTTERWAVE_API_VERSION" "2024-01-01" ".env.prod"
update_env_var "DEFAULT_PAYMENT_CURRENCY" "UGX" ".env.prod"
update_env_var "DEFAULT_PAYMENT_COUNTRY" "UG" ".env.prod"
update_env_var "DEFAULT_PAYMENT_OPTIONS" "card,mobile_money,mpesa,bank transfer" ".env.prod"
update_env_var "DEFAULT_REDIRECT_URL" "https://bottleplugug.com/payment/return" ".env.prod"

echo "📋 Updated Flutterwave configuration:"
echo "FLUTTERWAVE_ENVIRONMENT=$(grep '^FLUTTERWAVE_ENVIRONMENT=' .env.prod | cut -d'=' -f2)"
echo "FLUTTERWAVE_BASE_URL=$(grep '^FLUTTERWAVE_BASE_URL=' .env.prod | cut -d'=' -f2)"
echo "FLUTTERWAVE_API_VERSION=$(grep '^FLUTTERWAVE_API_VERSION=' .env.prod | cut -d'=' -f2)"

# Restart backend service to apply changes
echo "🔄 Restarting backend service..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.prod.yml --env-file .env.prod restart backend
    echo "✅ Backend service restarted"
else
    echo "⚠️ docker-compose not found. Please restart the backend service manually:"
    echo "   docker-compose -f docker-compose.prod.yml --env-file .env.prod restart backend"
fi

# Verify the configuration is loaded correctly
echo "🔍 Verifying configuration..."
sleep 5

if command -v docker-compose &> /dev/null; then
    echo "Testing Flutterwave configuration in Django..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python -c "
from django.conf import settings
print('✅ FLUTTERWAVE_ENVIRONMENT:', settings.FLUTTERWAVE_ENVIRONMENT)
print('✅ FLUTTERWAVE_BASE_URL:', settings.FLUTTERWAVE_BASE_URL)
print('✅ FLUTTERWAVE_API_VERSION:', settings.FLUTTERWAVE_API_VERSION)
print('✅ DEFAULT_PAYMENT_CURRENCY:', settings.DEFAULT_PAYMENT_CURRENCY)
" 2>/dev/null || echo "⚠️ Could not verify Django settings. Check manually."
fi

echo "🎉 Flutterwave production configuration fix completed!"
echo "📝 Summary:"
echo "   - Base URL: $PRODUCTION_BASE_URL"
echo "   - Environment: production"
echo "   - API Version: 2024-01-01 (v4)"
echo "   - OAuth Token URL: $OAUTH_TOKEN_URL"
echo ""
echo "💡 This script can be run after any deployment to ensure correct configuration."
