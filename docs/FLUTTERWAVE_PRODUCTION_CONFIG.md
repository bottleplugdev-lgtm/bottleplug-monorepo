# Flutterwave Production Configuration

This document explains the permanent solution for Flutterwave v4 API configuration that prevents production settings from being overwritten by deployments.

## 🚨 Problem Solved

Previously, the Flutterwave production configuration was using incorrect API URLs:
- ❌ **Wrong**: `https://api.flutterwave.com`
- ✅ **Correct**: `https://f4bexperience.flutterwave.com` (Official v4 URL)

This caused payment failures in production because the v4 API uses different endpoints than v3.

## 🔧 Solution Components

### 1. Production Configuration File
**File**: `backend/tanna_backend/production_config.py`

This file contains the official Flutterwave v4 API endpoints and is version-controlled to ensure it's never lost:

```python
FLUTTERWAVE_V4_PRODUCTION_CONFIG = {
    'base_url': 'https://f4bexperience.flutterwave.com',
    'oauth_token_url': 'https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token',
    'api_version': '2024-01-01',
    'environment': 'production'
}
```

### 2. Automatic Fix Script
**File**: `scripts/fix_production_flutterwave.sh`

This script automatically applies the correct configuration after each deployment:

```bash
# Run manually if needed
./scripts/fix_production_flutterwave.sh
```

### 3. Updated Django Settings
**File**: `backend/tanna_backend/settings.py`

The settings now automatically load the production configuration when in production mode.

### 4. Deployment Integration
**File**: `.github/workflows/deploy.yml`

The deployment workflow now automatically runs the fix script after each deployment.

## 🎯 How It Works

1. **During Development**: Uses sandbox configuration
2. **During Production**: Automatically loads production configuration from `production_config.py`
3. **During Deployment**: Runs fix script to ensure correct settings
4. **Manual Fix**: Can run the script manually if needed

## 🔍 Verification

To verify the configuration is correct:

```bash
# SSH to production server
ssh root@146.190.126.50
cd /opt/bottleplug

# Check current configuration
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec backend python -c "
from django.conf import settings
print('Environment:', settings.FLUTTERWAVE_ENVIRONMENT)
print('Base URL:', settings.FLUTTERWAVE_BASE_URL)
print('API Version:', settings.FLUTTERWAVE_API_VERSION)
"
```

**Expected Output:**
```
Environment: production
Base URL: https://f4bexperience.flutterwave.com
API Version: 2024-01-01
```

## 🛡️ Protection Mechanisms

1. **Version Control**: Configuration files are tracked in git
2. **Automatic Deployment Fix**: Script runs after every deployment
3. **Fallback Logic**: Settings.py has fallback to correct URLs
4. **Manual Recovery**: Script can be run manually anytime

## 🚀 Manual Fix (If Needed)

If you ever need to manually fix the configuration:

```bash
# SSH to production server
ssh root@146.190.126.50
cd /opt/bottleplug

# Run the fix script
./scripts/fix_production_flutterwave.sh

# Or apply manually
sed -i 's|FLUTTERWAVE_BASE_URL=.*|FLUTTERWAVE_BASE_URL=https://f4bexperience.flutterwave.com|' .env.prod
docker-compose -f docker-compose.prod.yml --env-file .env.prod restart backend
```

## 📋 Configuration Summary

| Setting | Production Value |
|---------|------------------|
| Environment | `production` |
| Base URL | `https://f4bexperience.flutterwave.com` |
| OAuth URL | `https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token` |
| API Version | `2024-01-01` |
| Currency | `UGX` |
| Country | `UG` |

## 🔐 Security Notes

- OAuth credentials are still loaded from environment variables
- Only the API endpoints are hardcoded in the configuration file
- Sensitive data remains in `.env.prod` (not version controlled)

## 🎉 Result

✅ **Flutterwave payments now work correctly in production**  
✅ **Configuration is protected from future deployments**  
✅ **Automatic fixes ensure consistency**  
✅ **Manual recovery options available**
