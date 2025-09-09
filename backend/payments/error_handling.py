"""
Flutterwave API Error Handling Module
Handles API errors, validation, and provides meaningful error messages
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


class FlutterwaveError:
    """
    Flutterwave API Error Handler
    """
    
    # Error code mappings
    ERROR_CODES = {
        '10400': {
            'type': 'REQUEST_NOT_VALID',
            'definition': 'The request was rejected due to invalid parameters or missing data',
            'possible_causes': [
                'Malformed request',
                'Missing parameters',
                'Invalid JSON payload',
                'Invalid card number',
                'Invalid payment method',
                'Invalid amount format'
            ],
            'suggestions': [
                'Check request format and required fields',
                'Validate card data before sending',
                'Ensure all required parameters are present',
                'Verify JSON structure is correct'
            ]
        },
        '10401': {
            'type': 'UNAUTHORIZATION',
            'definition': 'The request requires authentication or has invalid credentials',
            'possible_causes': [
                'Missing API key',
                'Expired token',
                'Incorrect credentials',
                'Invalid OAuth token',
                'Token not provided'
            ],
            'suggestions': [
                'Check API credentials configuration',
                'Verify OAuth token is valid and not expired',
                'Ensure Authorization header is present',
                'Regenerate access token if needed'
            ]
        },
        '10403': {
            'type': 'FORBIDDEN',
            'definition': 'The client does not have permission to access the resource',
            'possible_causes': [
                'Insufficient privileges',
                'Access restrictions',
                'Account suspended',
                'IP whitelist restrictions',
                'Rate limiting exceeded'
            ],
            'suggestions': [
                'Check account permissions and status',
                'Verify IP address is whitelisted',
                'Contact support for access issues',
                'Check rate limiting status'
            ]
        },
        '10404': {
            'type': 'RESOURCE_NOT_FOUND',
            'definition': 'The requested resource could not be found on the server',
            'possible_causes': [
                'Nonexistent endpoint',
                'Incorrect URL',
                'Deleted resource',
                'Invalid transaction reference',
                'Payment not found'
            ],
            'suggestions': [
                'Verify API endpoint URL',
                'Check transaction reference exists',
                'Ensure resource has not been deleted',
                'Validate API version compatibility'
            ]
        },
        '10409': {
            'type': 'RESOURCE_CONFLICT',
            'definition': 'A conflict occurred due to duplicate or conflicting data',
            'possible_causes': [
                'Attempt to create existing resource',
                'Version conflict',
                'Duplicate transaction reference',
                'Idempotency key conflict',
                'Concurrent modification'
            ],
            'suggestions': [
                'Use unique transaction references',
                'Implement proper idempotency handling',
                'Check for existing resources before creation',
                'Handle concurrent access properly'
            ]
        },
        '10422': {
            'type': 'UNPROCESSABLE',
            'definition': 'The request was well-formed but contained invalid data',
            'possible_causes': [
                'Failed validation',
                'Incorrect or incomplete fields',
                'Invalid card details',
                'Invalid phone number format',
                'Amount exceeds limits'
            ],
            'suggestions': [
                'Validate all input fields',
                'Check card number format and validity',
                'Verify phone number format',
                'Ensure amount is within limits',
                'Review validation error details'
            ]
        },
        '10500': {
            'type': 'INTERNAL_SERVER_ERROR',
            'definition': 'An unexpected server error occurred while processing the request',
            'possible_causes': [
                'System failure',
                'Unhandled exceptions',
                'Database connection issues',
                'Third-party service failures',
                'Temporary system issues'
            ],
            'suggestions': [
                'Retry the request after a delay',
                'Check Flutterwave service status',
                'Contact support if issue persists',
                'Implement exponential backoff',
                'Log error for investigation'
            ]
        }
    }
    
    def __init__(self, response=None, error_data=None):
        """
        Initialize error handler
        
        Args:
            response: HTTP response object
            error_data: Error data from API response
        """
        self.response = response
        self.error_data = error_data or {}
        self.status_code = getattr(response, 'status_code', None) if response else None
        
        # Parse error information
        self.status = self.error_data.get('status', 'failed')
        self.error_type = self.error_data.get('error', {}).get('type', 'UNKNOWN_ERROR')
        self.error_code = self.error_data.get('error', {}).get('code', '10000')
        self.error_message = self.error_data.get('error', {}).get('message', 'Unknown error occurred')
        self.validation_errors = self.error_data.get('error', {}).get('validation_errors', [])
    
    def get_error_info(self) -> Dict[str, Any]:
        """
        Get comprehensive error information
        
        Returns:
            dict: Complete error information
        """
        error_info = self.ERROR_CODES.get(self.error_code, {})
        
        return {
            'status_code': self.status_code,
            'status': self.status,
            'error_type': self.error_type,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'validation_errors': self.validation_errors,
            'definition': error_info.get('definition', 'Unknown error'),
            'possible_causes': error_info.get('possible_causes', []),
            'suggestions': error_info.get('suggestions', []),
            'is_retryable': self._is_retryable(),
            'is_validation_error': self._is_validation_error(),
            'is_authentication_error': self._is_authentication_error(),
            'is_permanent_error': self._is_permanent_error()
        }
    
    def _is_retryable(self) -> bool:
        """
        Check if error is retryable
        
        Returns:
            bool: True if error can be retried
        """
        retryable_codes = ['10500']  # Internal server errors
        return self.error_code in retryable_codes
    
    def _is_validation_error(self) -> bool:
        """
        Check if error is a validation error
        
        Returns:
            bool: True if validation error
        """
        validation_codes = ['10400', '10422']
        return self.error_code in validation_codes
    
    def _is_authentication_error(self) -> bool:
        """
        Check if error is an authentication error
        
        Returns:
            bool: True if authentication error
        """
        auth_codes = ['10401']
        return self.error_code in auth_codes
    
    def _is_permanent_error(self) -> bool:
        """
        Check if error is permanent (should not be retried)
        
        Returns:
            bool: True if permanent error
        """
        permanent_codes = ['10400', '10401', '10403', '10404', '10409', '10422']
        return self.error_code in permanent_codes
    
    def get_user_friendly_message(self) -> str:
        """
        Get user-friendly error message
        
        Returns:
            str: User-friendly error message
        """
        if self._is_validation_error():
            if self.validation_errors:
                # Return first validation error
                first_error = self.validation_errors[0]
                field = first_error.get('field', 'input')
                message = first_error.get('message', 'Invalid input')
                return f"{field.title()}: {message}"
            else:
                return self.error_message
        
        elif self._is_authentication_error():
            return "Authentication failed. Please check your credentials and try again."
        
        elif self._is_permanent_error():
            return f"Request failed: {self.error_message}"
        
        else:
            return "An unexpected error occurred. Please try again later."
    
    def get_log_message(self) -> str:
        """
        Get detailed log message for debugging
        
        Returns:
            str: Detailed log message
        """
        return (f"Flutterwave API Error - Code: {self.error_code}, "
                f"Type: {self.error_type}, Message: {self.error_message}, "
                f"Status: {self.status_code}")
    
    def should_retry(self, attempt: int = 1, max_attempts: int = 3) -> bool:
        """
        Determine if request should be retried
        
        Args:
            attempt (int): Current attempt number
            max_attempts (int): Maximum number of attempts
        
        Returns:
            bool: True if should retry
        """
        if attempt >= max_attempts:
            return False
        
        if not self._is_retryable():
            return False
        
        return True
    
    def get_retry_delay(self, attempt: int = 1) -> int:
        """
        Get retry delay in seconds (exponential backoff)
        
        Args:
            attempt (int): Current attempt number
        
        Returns:
            int: Delay in seconds
        """
        return min(2 ** attempt, 60)  # Max 60 seconds


class FlutterwaveErrorHandler:
    """
    Flutterwave API Error Handler with retry logic
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_response(self, response, context: str = "API request") -> Tuple[bool, Dict[str, Any]]:
        """
        Handle API response and determine success/failure
        
        Args:
            response: HTTP response object
            context (str): Context for logging
        
        Returns:
            tuple: (success, result_data)
        """
        try:
            if response.status_code in [200, 201]:
                # Success response
                data = response.json()
                return True, {
                    'success': True,
                    'data': data,
                    'status_code': response.status_code
                }
            
            elif response.status_code in [400, 401, 403, 404, 409, 422, 500]:
                # Error response
                error_data = response.json()
                error_handler = FlutterwaveError(response, error_data)
                error_info = error_handler.get_error_info()
                
                # Log error
                self.logger.error(f"{context} failed: {error_handler.get_log_message()}")
                
                return False, {
                    'success': False,
                    'error': error_info,
                    'user_message': error_handler.get_user_friendly_message(),
                    'status_code': response.status_code,
                    'retryable': error_handler._is_retryable()
                }
            
            else:
                # Unexpected status code
                self.logger.error(f"{context} failed with unexpected status: {response.status_code}")
                return False, {
                    'success': False,
                    'error': {
                        'error_code': '10000',
                        'error_message': f'Unexpected status code: {response.status_code}',
                        'status_code': response.status_code
                    },
                    'user_message': 'An unexpected error occurred',
                    'status_code': response.status_code,
                    'retryable': False
                }
        
        except Exception as e:
            # Exception during response handling
            self.logger.error(f"{context} failed with exception: {str(e)}")
            return False, {
                'success': False,
                'error': {
                    'error_code': '10000',
                    'error_message': f'Response parsing failed: {str(e)}',
                    'status_code': getattr(response, 'status_code', None)
                },
                'user_message': 'Failed to process response',
                'status_code': getattr(response, 'status_code', None),
                'retryable': False
            }
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate payment data before sending to API
        
        Args:
            payment_data (dict): Payment data to validate
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        required_fields = ['amount', 'currency', 'tx_ref']
        for field in required_fields:
            if field not in payment_data or not payment_data[field]:
                errors.append(f"{field.title()} is required")
        
        # Amount validation
        if 'amount' in payment_data:
            try:
                amount = float(payment_data['amount'])
                if amount <= 0:
                    errors.append("Amount must be greater than 0")
            except (ValueError, TypeError):
                errors.append("Amount must be a valid number")
        
        # Currency validation
        if 'currency' in payment_data:
            currency = payment_data['currency']
            if not currency or len(currency) != 3:
                errors.append("Currency must be a 3-letter code (e.g., UGX)")
        
        # Transaction reference validation
        if 'tx_ref' in payment_data:
            tx_ref = payment_data['tx_ref']
            if not tx_ref or len(tx_ref) < 3:
                errors.append("Transaction reference must be at least 3 characters")
        
        # Customer validation
        if 'customer' in payment_data:
            customer = payment_data['customer']
            if not isinstance(customer, dict):
                errors.append("Customer must be an object")
            else:
                if 'email' in customer and not self._is_valid_email(customer['email']):
                    errors.append("Customer email must be valid")
        
        return len(errors) == 0, errors
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Basic email validation
        
        Args:
            email (str): Email to validate
        
        Returns:
            bool: True if valid email
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of all error codes and their meanings
        
        Returns:
            dict: Error code summary
        """
        return {
            'error_codes': FlutterwaveError.ERROR_CODES,
            'total_codes': len(FlutterwaveError.ERROR_CODES),
            'validation_errors': ['10400', '10422'],
            'authentication_errors': ['10401'],
            'permission_errors': ['10403'],
            'not_found_errors': ['10404'],
            'conflict_errors': ['10409'],
            'server_errors': ['10500']
        } 