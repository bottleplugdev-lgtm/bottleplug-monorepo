from django.core.management.base import BaseCommand
from payments.error_handling import FlutterwaveError, FlutterwaveErrorHandler
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave error handling functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-error-codes',
            action='store_true',
            help='Test all error codes and their handling',
        )
        parser.add_argument(
            '--test-validation',
            action='store_true',
            help='Test payment data validation',
        )
        parser.add_argument(
            '--test-response-handling',
            action='store_true',
            help='Test response handling with mock responses',
        )
        parser.add_argument(
            '--list-errors',
            action='store_true',
            help='List all error codes and their meanings',
        )

    def handle(self, *args, **options):
        test_error_codes = options['test_error_codes']
        test_validation = options['test_validation']
        test_response_handling = options['test_response_handling']
        list_errors = options['list_errors']
        
        self.stdout.write('Testing Flutterwave Error Handling')
        
        # List errors if requested
        if list_errors:
            self._list_errors()
            return
        
        # Test specific functionality or run comprehensive tests
        if test_error_codes:
            self._test_error_codes()
        elif test_validation:
            self._test_validation()
        elif test_response_handling:
            self._test_response_handling()
        else:
            # Run all tests
            self._test_error_codes()
            self._test_validation()
            self._test_response_handling()
    
    def _list_errors(self):
        """List all error codes and their meanings"""
        self.stdout.write('\n=== Flutterwave Error Codes ===')
        
        error_handler = FlutterwaveErrorHandler()
        error_summary = error_handler.get_error_summary()
        
        self.stdout.write(f'Total Error Codes: {error_summary["total_codes"]}')
        
        for code, info in error_summary['error_codes'].items():
            self.stdout.write(f'\nCode: {code}')
            self.stdout.write(f'Type: {info["type"]}')
            self.stdout.write(f'Definition: {info["definition"]}')
            
            self.stdout.write('Possible Causes:')
            for cause in info['possible_causes']:
                self.stdout.write(f'  • {cause}')
            
            self.stdout.write('Suggestions:')
            for suggestion in info['suggestions']:
                self.stdout.write(f'  • {suggestion}')
    
    def _test_error_codes(self):
        """Test all error codes and their handling"""
        self.stdout.write('\n=== Testing Error Codes ===')
        
        # Test each error code
        for code in FlutterwaveError.ERROR_CODES.keys():
            self.stdout.write(f'\n--- Testing Error Code: {code} ---')
            
            # Create mock error response
            mock_response = type('MockResponse', (), {
                'status_code': self._get_status_code_for_error(code)
            })()
            
            mock_error_data = {
                'status': 'failed',
                'error': {
                    'type': FlutterwaveError.ERROR_CODES[code]['type'],
                    'code': code,
                    'message': f'Test error for code {code}',
                    'validation_errors': []
                }
            }
            
            # Create error handler
            error_handler = FlutterwaveError(mock_response, mock_error_data)
            error_info = error_handler.get_error_info()
            
            self.stdout.write(f'Error Code: {error_info["error_code"]}')
            self.stdout.write(f'Error Type: {error_info["error_type"]}')
            self.stdout.write(f'Error Message: {error_info["error_message"]}')
            self.stdout.write(f'Definition: {error_info["definition"]}')
            
            # Test error classification
            self.stdout.write(f'Is Retryable: {error_info["is_retryable"]}')
            self.stdout.write(f'Is Validation Error: {error_info["is_validation_error"]}')
            self.stdout.write(f'Is Authentication Error: {error_info["is_authentication_error"]}')
            self.stdout.write(f'Is Permanent Error: {error_info["is_permanent_error"]}')
            
            # Test user-friendly message
            user_message = error_handler.get_user_friendly_message()
            self.stdout.write(f'User Message: {user_message}')
            
            # Test retry logic
            should_retry = error_handler.should_retry(attempt=1, max_attempts=3)
            retry_delay = error_handler.get_retry_delay(attempt=1)
            self.stdout.write(f'Should Retry: {should_retry}')
            self.stdout.write(f'Retry Delay: {retry_delay}s')
    
    def _test_validation(self):
        """Test payment data validation"""
        self.stdout.write('\n=== Testing Payment Data Validation ===')
        
        error_handler = FlutterwaveErrorHandler()
        
        # Test valid payment data
        valid_payment = {
            'amount': '1000',
            'currency': 'UGX',
            'tx_ref': 'TEST_REF_123',
            'customer': {
                'email': 'test@example.com',
                'name': 'Test Customer'
            }
        }
        
        is_valid, errors = error_handler.validate_payment_data(valid_payment)
        self.stdout.write(f'\nValid Payment Data:')
        self.stdout.write(f'  Is Valid: {is_valid}')
        if errors:
            self.stdout.write(f'  Errors: {errors}')
        else:
            self.stdout.write('  ✅ No validation errors')
        
        # Test invalid payment data
        invalid_payment = {
            'amount': '-100',  # Invalid amount
            'currency': 'UG',  # Invalid currency
            'tx_ref': 'AB',    # Too short
            'customer': {
                'email': 'invalid-email',  # Invalid email
                'name': 'Test Customer'
            }
        }
        
        is_valid, errors = error_handler.validate_payment_data(invalid_payment)
        self.stdout.write(f'\nInvalid Payment Data:')
        self.stdout.write(f'  Is Valid: {is_valid}')
        if errors:
            self.stdout.write('  Errors:')
            for error in errors:
                self.stdout.write(f'    ❌ {error}')
        else:
            self.stdout.write('  ✅ No validation errors (unexpected)')
        
        # Test missing required fields
        incomplete_payment = {
            'amount': '1000'
            # Missing currency and tx_ref
        }
        
        is_valid, errors = error_handler.validate_payment_data(incomplete_payment)
        self.stdout.write(f'\nIncomplete Payment Data:')
        self.stdout.write(f'  Is Valid: {is_valid}')
        if errors:
            self.stdout.write('  Errors:')
            for error in errors:
                self.stdout.write(f'    ❌ {error}')
        else:
            self.stdout.write('  ✅ No validation errors (unexpected)')
    
    def _test_response_handling(self):
        """Test response handling with mock responses"""
        self.stdout.write('\n=== Testing Response Handling ===')
        
        error_handler = FlutterwaveErrorHandler()
        
        # Test successful response
        class MockSuccessResponse:
            status_code = 200
            def json(self):
                return {
                    'status': 'success',
                    'data': {
                        'reference': 'TEST_REF_123',
                        'link': 'https://example.com/pay'
                    }
                }
        
        success, result = error_handler.handle_response(
            MockSuccessResponse(), 
            "Test successful payment"
        )
        
        self.stdout.write(f'\nSuccessful Response:')
        self.stdout.write(f'  Success: {success}')
        if success:
            self.stdout.write('  ✅ Success response handled correctly')
            self.stdout.write(f'  Data: {result["data"]}')
        else:
            self.stdout.write('  ❌ Success response not handled correctly')
        
        # Test error response
        class MockErrorResponse:
            status_code = 400
            def json(self):
                return {
                    'status': 'failed',
                    'error': {
                        'type': 'REQUEST_NOT_VALID',
                        'code': '10400',
                        'message': 'Invalid card number',
                        'validation_errors': [
                            {
                                'field': 'card_number',
                                'message': 'Card number is required'
                            }
                        ]
                    }
                }
        
        success, result = error_handler.handle_response(
            MockErrorResponse(), 
            "Test error payment"
        )
        
        self.stdout.write(f'\nError Response:')
        self.stdout.write(f'  Success: {success}')
        if not success:
            self.stdout.write('  ✅ Error response handled correctly')
            self.stdout.write(f'  Error Code: {result["error"]["error_code"]}')
            self.stdout.write(f'  Error Type: {result["error"]["error_type"]}')
            self.stdout.write(f'  User Message: {result["user_message"]}')
            self.stdout.write(f'  Retryable: {result["retryable"]}')
        else:
            self.stdout.write('  ❌ Error response not handled correctly')
        
        # Test server error response
        class MockServerErrorResponse:
            status_code = 500
            def json(self):
                return {
                    'status': 'failed',
                    'error': {
                        'type': 'INTERNAL_SERVER_ERROR',
                        'code': '10500',
                        'message': 'An unexpected server error occurred',
                        'validation_errors': []
                    }
                }
        
        success, result = error_handler.handle_response(
            MockServerErrorResponse(), 
            "Test server error"
        )
        
        self.stdout.write(f'\nServer Error Response:')
        self.stdout.write(f'  Success: {success}')
        if not success:
            self.stdout.write('  ✅ Server error handled correctly')
            self.stdout.write(f'  Error Code: {result["error"]["error_code"]}')
            self.stdout.write(f'  Retryable: {result["retryable"]}')
            if result["retryable"]:
                self.stdout.write('  ✅ Server error marked as retryable')
            else:
                self.stdout.write('  ❌ Server error should be retryable')
        else:
            self.stdout.write('  ❌ Server error not handled correctly')
    
    def _get_status_code_for_error(self, error_code: str) -> int:
        """Get HTTP status code for error code"""
        status_code_mapping = {
            '10400': 400,  # Bad Request
            '10401': 401,  # Unauthorized
            '10403': 403,  # Forbidden
            '10404': 404,  # Not Found
            '10409': 409,  # Conflict
            '10422': 422,  # Unprocessable Entity
            '10500': 500,  # Internal Server Error
        }
        return status_code_mapping.get(error_code, 400)
    
    def _test_email_validation(self):
        """Test email validation"""
        self.stdout.write('\n=== Testing Email Validation ===')
        
        error_handler = FlutterwaveErrorHandler()
        
        test_emails = [
            'test@example.com',      # Valid
            'user.name@domain.co.uk', # Valid
            'invalid-email',          # Invalid
            'test@',                 # Invalid
            '@example.com',          # Invalid
            'test@example',          # Invalid
            '',                      # Invalid
        ]
        
        for email in test_emails:
            is_valid = error_handler._is_valid_email(email)
            status = '✅' if is_valid else '❌'
            self.stdout.write(f'{status} {email}')
    
    def _test_comprehensive_error_handling(self):
        """Test comprehensive error handling scenarios"""
        self.stdout.write('\n=== Testing Comprehensive Error Handling ===')
        
        # Test all error codes with different scenarios
        scenarios = [
            {
                'name': 'Validation Error with Details',
                'error_code': '10400',
                'validation_errors': [
                    {'field': 'card_number', 'message': 'Card number is required'},
                    {'field': 'cvv', 'message': 'CVV must be 3-4 digits'}
                ]
            },
            {
                'name': 'Authentication Error',
                'error_code': '10401',
                'validation_errors': []
            },
            {
                'name': 'Permission Error',
                'error_code': '10403',
                'validation_errors': []
            },
            {
                'name': 'Resource Not Found',
                'error_code': '10404',
                'validation_errors': []
            },
            {
                'name': 'Conflict Error',
                'error_code': '10409',
                'validation_errors': []
            },
            {
                'name': 'Unprocessable Entity',
                'error_code': '10422',
                'validation_errors': [
                    {'field': 'amount', 'message': 'Amount exceeds maximum limit'}
                ]
            },
            {
                'name': 'Server Error',
                'error_code': '10500',
                'validation_errors': []
            }
        ]
        
        for scenario in scenarios:
            self.stdout.write(f'\n--- {scenario["name"]} ---')
            
            # Create mock response
            mock_response = type('MockResponse', (), {
                'status_code': self._get_status_code_for_error(scenario['error_code'])
            })()
            
            mock_error_data = {
                'status': 'failed',
                'error': {
                    'type': FlutterwaveError.ERROR_CODES[scenario['error_code']]['type'],
                    'code': scenario['error_code'],
                    'message': f'Test error for {scenario["name"]}',
                    'validation_errors': scenario['validation_errors']
                }
            }
            
            # Test error handling
            error_handler = FlutterwaveError(mock_response, mock_error_data)
            error_info = error_handler.get_error_info()
            
            self.stdout.write(f'Error Code: {error_info["error_code"]}')
            self.stdout.write(f'Error Type: {error_info["error_type"]}')
            self.stdout.write(f'Is Retryable: {error_info["is_retryable"]}')
            self.stdout.write(f'User Message: {error_handler.get_user_friendly_message()}')
            
            if error_info['validation_errors']:
                self.stdout.write('Validation Errors:')
                for error in error_info['validation_errors']:
                    self.stdout.write(f'  • {error["field"]}: {error["message"]}')
        
        self.stdout.write('\n✅ Comprehensive error handling test completed') 