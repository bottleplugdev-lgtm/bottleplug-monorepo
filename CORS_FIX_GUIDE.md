# CORS Fix for Live Web Frontend Connection Issue

## Problem Identified
Your live web frontend (`https://bottleplugug.com`) cannot connect to the live backend because the CORS configuration doesn't include your production domains.

## Root Cause
The backend CORS settings only included localhost development URLs, missing:
- `https://bottleplugug.com`
- `https://www.bottleplugug.com`
- `https://admin.bottleplugug.com`
- `https://dashboard.bottleplugug.com`

## Solution Applied

### 1. Updated Backend CORS Configuration
**File:** `backend/tanna_backend/settings.py`

Added production domains to `CORS_ALLOWED_ORIGINS`:
```python
CORS_ALLOWED_ORIGINS = [
    # Development origins (existing)
    "http://localhost:3000",
    "http://localhost:3001",
    # ... other localhost entries
    
    # Production origins (NEW)
    "https://bottleplugug.com",
    "https://www.bottleplugug.com",
    "https://admin.bottleplugug.com",
    "https://dashboard.bottleplugug.com",
]
```

### 2. Updated ALLOWED_HOSTS
**File:** `backend/tanna_backend/settings.py`

Added production domains to `ALLOWED_HOSTS`:
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,bottleplugug.com,www.bottleplugug.com,api.bottleplugug.com,admin.bottleplugug.com,dashboard.bottleplugug.com,docs.bottleplugug.com,db.bottleplugug.com', cast=lambda v: [s.strip() for s in v.split(',')])
```

### 3. Updated Production Environment Template
**File:** `env.prod.template`

Updated with correct production domains and API URLs.

## Deployment Options

### Option 1: Automated Deployment (Recommended)
```bash
# Run the automated fix script
./scripts/fix_cors_deployment.sh
```

### Option 2: Manual Deployment
```bash
# 1. Stop current services
docker-compose -f docker-compose.prod.yml down

# 2. Update your .env.prod file with the new CORS settings
# Make sure these are set:
# ALLOWED_HOSTS=bottleplugug.com,www.bottleplugug.com,api.bottleplugug.com,admin.bottleplugug.com,dashboard.bottleplugug.com,docs.bottleplugug.com,db.bottleplugug.com,146.190.126.50
# CORS_ALLOWED_ORIGINS=https://bottleplugug.com,https://www.bottleplugug.com,https://admin.bottleplugug.com,https://dashboard.bottleplugug.com

# 3. Rebuild and restart services
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify the fix
curl -H "Origin: https://bottleplugug.com" -H "Authorization: Bearer bottleplug-web-token-2024" https://api.bottleplugug.com/api/v1/products/categories/
```

### Option 3: Quick Backend Restart (If settings are already deployed)
```bash
# Just restart the backend service to pick up the new CORS settings
docker-compose -f docker-compose.prod.yml restart backend
```

## Verification Steps

After deployment, verify the fix works:

1. **Test API Health:**
   ```bash
   curl https://api.bottleplugug.com/api/health/
   ```

2. **Test CORS from Main Domain:**
   ```bash
   curl -H "Origin: https://bottleplugug.com" -H "Authorization: Bearer bottleplug-web-token-2024" https://api.bottleplugug.com/api/v1/products/categories/
   ```

3. **Test Frontend Connection:**
   - Visit `https://bottleplugug.com`
   - Open browser developer tools (F12)
   - Check Network tab for API calls
   - Should see successful API responses instead of CORS errors

## Expected Results

After applying this fix:
- ✅ Live web frontend can connect to live backend
- ✅ API calls from `https://bottleplugug.com` will work
- ✅ CORS errors in browser console will be resolved
- ✅ All production domains are properly configured

## Rollback Instructions

If you need to rollback:
```bash
# Restore backup settings
cp backend/tanna_backend/settings.py.backup.* backend/tanna_backend/settings.py

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

## Additional Notes

- The backend API is working correctly (verified with curl tests)
- Frontend configuration is correct (using proper API base URL)
- SSL certificates are valid and working
- Authentication is working properly
- The only issue was missing CORS configuration for production domains

## Support

If you encounter any issues during deployment:
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verify environment variables: `docker-compose -f docker-compose.prod.yml config`
3. Test individual services: `docker-compose -f docker-compose.prod.yml ps`
