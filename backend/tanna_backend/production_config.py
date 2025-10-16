"""
Production-specific configuration for Bottleplug
This file contains production settings that should never be overwritten by deployments.
It's loaded by settings.py when DJANGO_SETTINGS_MODULE includes production settings.
"""

# Flutterwave v4 Production Configuration
# These URLs are the official v4 API endpoints and should not be changed
FLUTTERWAVE_V4_PRODUCTION_CONFIG = {
    'base_url': 'https://f4bexperience.flutterwave.com',
    'oauth_token_url': 'https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token',
    'api_version': '2024-01-01',
    'environment': 'production'
}

FLUTTERWAVE_V4_SANDBOX_CONFIG = {
    'base_url': 'https://developersandbox-api.flutterwave.com',
    'oauth_token_url': 'https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token',
    'api_version': '2024-01-01',
    'environment': 'sandbox'
}

# Legacy v3 API Configuration (for fallback)
FLUTTERWAVE_V3_PRODUCTION_CONFIG = {
    'base_url': 'https://api.flutterwave.com/v3',
    'api_version': '2023-01-01',
    'environment': 'production'
}

FLUTTERWAVE_V3_SANDBOX_CONFIG = {
    'base_url': 'https://api.flutterwave.com/v3',
    'api_version': '2023-01-01',
    'environment': 'sandbox'
}

def get_flutterwave_config(environment='production', api_version='2024-01-01'):
    """
    Get the correct Flutterwave configuration based on environment and API version
    
    Args:
        environment (str): 'production' or 'sandbox'
        api_version (str): '2024-01-01' (v4) or '2023-01-01' (v3)
    
    Returns:
        dict: Configuration dictionary with base_url, oauth_token_url, etc.
    """
    if api_version == '2024-01-01':  # v4 API
        if environment == 'production':
            return FLUTTERWAVE_V4_PRODUCTION_CONFIG
        else:
            return FLUTTERWAVE_V4_SANDBOX_CONFIG
    else:  # v3 API fallback
        if environment == 'production':
            return FLUTTERWAVE_V3_PRODUCTION_CONFIG
        else:
            return FLUTTERWAVE_V3_SANDBOX_CONFIG

# Production-specific overrides
PRODUCTION_OVERRIDES = {
    # Ensure production environment is always set correctly
    'FLUTTERWAVE_ENVIRONMENT': 'production',
    
    # Force v4 API version for production
    'FLUTTERWAVE_API_VERSION': '2024-01-01',
    
    # Production payment settings
    'DEFAULT_PAYMENT_CURRENCY': 'UGX',
    'DEFAULT_PAYMENT_COUNTRY': 'UG',
    'DEFAULT_PAYMENT_OPTIONS': 'card,mobile_money,mpesa,bank transfer',
    
    # Production redirect URL
    'DEFAULT_REDIRECT_URL': 'https://bottleplugug.com/payment/return',
}
