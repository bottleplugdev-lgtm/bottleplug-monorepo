# Environment Setup Guide

This guide explains how to set up the development and production environments for the Bottleplug project.

## Environment Files

### Development Environment (`.env.dev`)
Used for local development with Flutterwave sandbox API.

### Production Environment (`.env.prod`)
Used for production deployment with Flutterwave live API.

## Flutterwave Configuration

### Development/Sandbox
- **Base URL**: `https://developersandbox-api.flutterwave.com`
- **OAuth URL**: `https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token`
- **API Version**: v4 (2024-01-01)
- **Authentication**: OAuth 2.0 Client Credentials

### Production/Live
- **Base URL**: `https://f4bexperience.flutterwave.com`
- **OAuth URL**: `https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token`
- **API Version**: v4 (2024-01-01)
- **Authentication**: OAuth 2.0 Client Credentials

## Required Environment Variables

### Flutterwave Settings
```bash
# Client credentials from Flutterwave dashboard
FLW_CLIENT_ID=your-client-id
FLW_CLIENT_SECRET=your-client-secret
FLUTTERWAVE_ENCRYPTION_KEY=your-encryption-key

# API URLs (automatically set based on environment)
FLUTTERWAVE_BASE_URL=https://developersandbox-api.flutterwave.com  # or production URL
FLUTTERWAVE_OAUTH_TOKEN_URL=https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token
```

### Database Settings
```bash
DB_NAME=bottleplug_dev  # or bottleplug_prod
DB_USER=bottleplug_user
DB_PASSWORD=your-db-password
DB_HOST=localhost  # or db for Docker
DB_PORT=5432
```

### Django Settings
```bash
DEBUG=True  # False for production
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1  # add production domains for prod
```

## Docker Compose Files

### Development (`docker-compose.yml`)
- Uses sandbox Flutterwave API
- Debug mode enabled
- Local volume mounts for development

### Production (`docker-compose.prod.yml`)
- Uses live Flutterwave API
- Production optimizations
- Health checks enabled

## Setup Instructions

### 1. Development Setup
```bash
# Copy and configure development environment
cp .env.dev .env
# Edit .env with your sandbox credentials

# Start development containers
docker-compose up -d
```

### 2. Production Setup
```bash
# Copy and configure production environment
cp .env.prod .env
# Edit .env with your production credentials

# Start production containers
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## Important Notes

1. **Never commit actual credentials** to version control
2. **Use sandbox credentials** for development
3. **Use production credentials** only on production server
4. **Environment variables override** Django settings
5. **OAuth 2.0 is required** for Flutterwave v4 API

## Troubleshooting

### Common Issues
1. **OAuth authentication fails**: Check client credentials and OAuth URL
2. **API calls return 404**: Verify base URL is correct for your environment
3. **Container startup fails**: Check environment variables are properly set

### Verification Commands
```bash
# Test OAuth authentication
docker-compose exec backend python -c "
from payments.auth_manager import FlutterwaveOAuthManager
auth = FlutterwaveOAuthManager()
token = auth.get_access_token()
print(f'Token obtained: {bool(token)}')
"

# Test API connectivity
docker-compose exec backend python -c "
from payments.services import FlutterwaveService
service = FlutterwaveService()
print(f'Base URL: {service.base_url}')
"
```
