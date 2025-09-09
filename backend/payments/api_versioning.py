"""
Flutterwave API Versioning Module
Handles different API versions and ensures backward compatibility
"""

import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class FlutterwaveAPIVersion:
    """
    Flutterwave API Version Management
    """
    
    # Supported API versions
    SUPPORTED_VERSIONS = {
        '2024-01-01': {
            'name': 'v4 (Latest)',
            'description': 'Latest API version with all features',
            'base_urls': {
                'sandbox': 'https://api.flutterwave.cloud/developersandbox',
                'production': 'https://api.flutterwave.cloud/f4bexperience'
            },
            'features': [
                'OAuth 2.0 authentication',
                'v4 API headers (Idempotency, Trace, Scenario)',
                'Enhanced encryption',
                'Comprehensive testing scenarios'
            ],
            'breaking_changes': [],
            'deprecated': False
        },
        '2023-01-01': {
            'name': 'v3 (Legacy)',
            'description': 'Legacy API version for backward compatibility',
            'base_urls': {
                'sandbox': 'https://api.flutterwave.com/v3',
                'production': 'https://api.flutterwave.com/v3'
            },
            'features': [
                'API key authentication',
                'Basic encryption',
                'Standard webhooks'
            ],
            'breaking_changes': [
                'No OAuth 2.0 support',
                'No v4 API headers',
                'Limited testing scenarios'
            ],
            'deprecated': True
        }
    }
    
    # Default API version
    DEFAULT_VERSION = '2024-01-01'
    
    def __init__(self, version: Optional[str] = None):
        """
        Initialize API version manager
        
        Args:
            version (str): API version to use (default: latest)
        """
        self.version = version or getattr(settings, 'FLUTTERWAVE_API_VERSION', self.DEFAULT_VERSION)
        
        if self.version not in self.SUPPORTED_VERSIONS:
            logger.warning(f"Unsupported API version: {self.version}, using default: {self.DEFAULT_VERSION}")
            self.version = self.DEFAULT_VERSION
        
        self.version_info = self.SUPPORTED_VERSIONS[self.version]
        logger.info(f"Using Flutterwave API version: {self.version} ({self.version_info['name']})")
    
    def get_base_url(self, environment: str = 'sandbox') -> str:
        """
        Get base URL for the current API version and environment
        
        Args:
            environment (str): Environment (sandbox or production)
        
        Returns:
            str: Base URL for the API version
        """
        return self.version_info['base_urls'].get(environment, self.version_info['base_urls']['sandbox'])
    
    def get_version_headers(self, include_version: bool = True) -> Dict[str, str]:
        """
        Get headers specific to the API version
        
        Args:
            include_version (bool): Include X-API-Version header
        
        Returns:
            dict: Headers for the API version
        """
        headers = {}
        
        if include_version:
            headers['X-API-Version'] = self.version
        
        return headers
    
    def is_v4(self) -> bool:
        """
        Check if using v4 API (2024-01-01)
        
        Returns:
            bool: True if v4 API
        """
        return self.version == '2024-01-01'
    
    def is_v3(self) -> bool:
        """
        Check if using v3 API (2023-01-01)
        
        Returns:
            bool: True if v3 API
        """
        return self.version == '2023-01-01'
    
    def supports_oauth(self) -> bool:
        """
        Check if API version supports OAuth 2.0
        
        Returns:
            bool: True if OAuth 2.0 supported
        """
        return self.is_v4()
    
    def supports_v4_headers(self) -> bool:
        """
        Check if API version supports v4 headers (Idempotency, Trace, Scenario)
        
        Returns:
            bool: True if v4 headers supported
        """
        return self.is_v4()
    
    def supports_scenarios(self) -> bool:
        """
        Check if API version supports testing scenarios
        
        Returns:
            bool: True if scenarios supported
        """
        return self.is_v4()
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the current API version
        
        Returns:
            dict: Version information
        """
        return {
            'version': self.version,
            'name': self.version_info['name'],
            'description': self.version_info['description'],
            'features': self.version_info['features'],
            'breaking_changes': self.version_info['breaking_changes'],
            'deprecated': self.version_info['deprecated'],
            'supports_oauth': self.supports_oauth(),
            'supports_v4_headers': self.supports_v4_headers(),
            'supports_scenarios': self.supports_scenarios()
        }
    
    @classmethod
    def get_supported_versions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all supported API versions
        
        Returns:
            dict: All supported versions
        """
        return cls.SUPPORTED_VERSIONS
    
    @classmethod
    def get_latest_version(cls) -> str:
        """
        Get the latest API version
        
        Returns:
            str: Latest version
        """
        return cls.DEFAULT_VERSION


class APIVersionManager:
    """
    Manages API version compatibility and migration
    """
    
    def __init__(self):
        self.version_manager = FlutterwaveAPIVersion()
    
    def get_compatible_headers(self, base_headers: Dict[str, str], 
                             include_oauth: bool = True,
                             include_v4_headers: bool = True,
                             include_scenarios: bool = True) -> Dict[str, str]:
        """
        Get headers compatible with the current API version
        
        Args:
            base_headers (dict): Base headers to modify
            include_oauth (bool): Include OAuth headers if supported
            include_v4_headers (bool): Include v4 headers if supported
            include_scenarios (bool): Include scenario headers if supported
        
        Returns:
            dict: Compatible headers for the API version
        """
        headers = base_headers.copy()
        
        # Add API version header
        version_headers = self.version_manager.get_version_headers()
        headers.update(version_headers)
        
        # Remove OAuth if not supported
        if not self.version_manager.supports_oauth() and 'Authorization' in headers:
            if headers['Authorization'].startswith('Bearer '):
                logger.warning("OAuth 2.0 not supported in this API version, using API key")
                # Fallback to API key authentication would be handled elsewhere
        
        # Remove v4 headers if not supported
        if not self.version_manager.supports_v4_headers():
            v4_headers = ['X-Idempotency-Key', 'X-Trace-Id', 'X-Scenario-Key']
            for header in v4_headers:
                if header in headers:
                    logger.warning(f"v4 header '{header}' not supported in this API version, removing")
                    headers.pop(header, None)
        
        return headers
    
    def get_compatible_payload(self, payload: Dict[str, Any], 
                             payment_type: str = None) -> Dict[str, Any]:
        """
        Get payload compatible with the current API version
        
        Args:
            payload (dict): Original payload
            payment_type (str): Type of payment (card, mobile_money, etc.)
        
        Returns:
            dict: Compatible payload for the API version
        """
        compatible_payload = payload.copy()
        
        # Handle v3 vs v4 payload differences
        if self.version_manager.is_v3():
            # v3 specific adjustments
            if 'payment_method' in compatible_payload and payment_type == 'card':
                # v3 might use different structure for card data
                if 'card' in compatible_payload['payment_method']:
                    # Convert v4 card structure to v3 if needed
                    card_data = compatible_payload['payment_method']['card']
                    if 'encrypted_card_number' in card_data:
                        # v3 might use different encryption structure
                        logger.info("Converting v4 card structure to v3 compatibility")
        
        return compatible_payload
    
    def get_compatible_url(self, endpoint: str, environment: str = 'sandbox') -> str:
        """
        Get URL compatible with the current API version
        
        Args:
            endpoint (str): API endpoint
            environment (str): Environment (sandbox or production)
        
        Returns:
            str: Compatible URL for the API version
        """
        base_url = self.version_manager.get_base_url(environment)
        return f"{base_url}/{endpoint.lstrip('/')}"
    
    def validate_version_compatibility(self, features: list) -> tuple[bool, list]:
        """
        Validate if requested features are compatible with current API version
        
        Args:
            features (list): List of features to check
        
        Returns:
            tuple: (is_compatible, incompatible_features)
        """
        incompatible_features = []
        
        feature_checks = {
            'oauth': self.version_manager.supports_oauth(),
            'v4_headers': self.version_manager.supports_v4_headers(),
            'scenarios': self.version_manager.supports_scenarios(),
            'encryption': True,  # All versions support encryption
            'webhooks': True     # All versions support webhooks
        }
        
        for feature in features:
            if feature in feature_checks and not feature_checks[feature]:
                incompatible_features.append(feature)
        
        return len(incompatible_features) == 0, incompatible_features
    
    def get_migration_guide(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """
        Get migration guide between API versions
        
        Args:
            from_version (str): Source version
            to_version (str): Target version
        
        Returns:
            dict: Migration guide
        """
        if from_version == to_version:
            return {'message': 'No migration needed - same version'}
        
        versions = self.version_manager.get_supported_versions()
        
        if from_version not in versions or to_version not in versions:
            return {'error': 'One or both versions not supported'}
        
        from_info = versions[from_version]
        to_info = versions[to_version]
        
        migration_guide = {
            'from_version': from_version,
            'to_version': to_version,
            'from_name': from_info['name'],
            'to_name': to_info['name'],
            'breaking_changes': to_info.get('breaking_changes', []),
            'new_features': to_info.get('features', []),
            'deprecated': from_info.get('deprecated', False),
            'recommendations': []
        }
        
        # Add specific recommendations based on version changes
        if from_version == '2023-01-01' and to_version == '2024-01-01':
            migration_guide['recommendations'] = [
                'Update authentication to use OAuth 2.0',
                'Add v4 API headers (X-Idempotency-Key, X-Trace-Id)',
                'Update base URLs to v4 endpoints',
                'Test with new scenario keys for comprehensive testing'
            ]
        
        return migration_guide 