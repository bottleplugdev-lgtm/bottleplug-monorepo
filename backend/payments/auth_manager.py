import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FlutterwaveAuthManager:
    """
    OAuth 2.0 Authentication Manager for Flutterwave API
    """
    
    def __init__(self):
        self.client_id = getattr(settings, 'FLW_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'FLW_CLIENT_SECRET', '')
        self.access_token = None
        self.expiry = None
        self.token_type = None
        
        if not self.client_id or not self.client_secret:
            logger.warning("Flutterwave OAuth credentials not configured - using fallback API key authentication")
    
    def generate_access_token(self):
        """
        Generate OAuth 2.0 access token from Flutterwave
        """
        try:
            if not self.client_id or not self.client_secret:
                logger.error("OAuth credentials not configured")
                return False
            
            url = 'https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token'
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                self.access_token = response_data.get('access_token')
                self.expiry = datetime.now() + timedelta(seconds=response_data.get('expires_in', 600))
                self.token_type = response_data.get('token_type', 'Bearer')
                
                logger.info("OAuth 2.0 access token generated successfully")
                return True
            else:
                logger.error(f"Failed to generate access token: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            return False
    
    def get_access_token(self):
        """
        Get current access token, generate new one if expired or not available
        """
        # Check if token exists and is not expired
        if self.access_token and self.expiry:
            # Refresh token if it expires in less than 1 minute
            if self.expiry - datetime.now() < timedelta(minutes=1):
                logger.info("Access token expiring soon, generating new token")
                self.generate_access_token()
        else:
            # No token available, generate new one
            logger.info("No access token available, generating new token")
            self.generate_access_token()
        
        return self.access_token
    
    def get_auth_headers(self):
        """
        Get headers with OAuth 2.0 Bearer token
        """
        token = self.get_access_token()
        if token:
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        else:
            # Fallback to API key authentication
            logger.warning("Using fallback API key authentication")
            return {
                'Authorization': f'Bearer {getattr(settings, "FLUTTERWAVE_SECRET_KEY", "")}',
                'Content-Type': 'application/json'
            }
    
    def generate_idempotency_key(self):
        """
        Generate a unique idempotency key for API requests
        Following Flutterwave best practices using UUID
        """
        import uuid
        
        # Use UUID as recommended by Flutterwave for uniqueness
        return str(uuid.uuid4())
    
    def generate_idempotency_key_with_prefix(self, prefix='flw'):
        """
        Generate a unique idempotency key with custom prefix
        """
        import uuid
        import time
        
        # Create a unique key using timestamp and UUID
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4()).replace('-', '')[:16]
        return f"{prefix}_{timestamp}_{unique_id}"
    
    def generate_trace_id(self):
        """
        Generate a unique trace ID for API request tracking
        """
        import uuid
        
        # Create a unique trace ID
        return f"trace_{str(uuid.uuid4()).replace('-', '')}"
    
    def get_v4_headers(self, include_idempotency=True, include_trace=True, scenario_key=None, custom_idempotency_key=None):
        """
        Get complete v4 API headers with all required fields
        
        Args:
            include_idempotency (bool): Include X-Idempotency-Key header
            include_trace (bool): Include X-Trace-Id header
            scenario_key (str): Optional scenario key for testing
            custom_idempotency_key (str): Custom idempotency key (if None, auto-generated)
        """
        base_headers = self.get_auth_headers()
        
        # Add idempotency key if requested
        if include_idempotency:
            if custom_idempotency_key:
                base_headers['X-Idempotency-Key'] = custom_idempotency_key
            else:
                base_headers['X-Idempotency-Key'] = self.generate_idempotency_key()
        
        # Add trace ID if requested
        if include_trace:
            base_headers['X-Trace-Id'] = self.generate_trace_id()
        
        # Add scenario key if provided (for testing)
        if scenario_key:
            base_headers['X-Scenario-Key'] = scenario_key
        
        return base_headers
    
    def is_oauth_configured(self):
        """
        Check if OAuth 2.0 credentials are properly configured
        """
        return bool(self.client_id and self.client_secret)
    
    def get_token_info(self):
        """
        Get current token information for debugging
        """
        return {
            'has_token': bool(self.access_token),
            'expires_at': self.expiry.isoformat() if self.expiry else None,
            'token_type': self.token_type,
            'is_oauth_configured': self.is_oauth_configured(),
            'time_until_expiry': (self.expiry - datetime.now()).total_seconds() if self.expiry else None
        } 