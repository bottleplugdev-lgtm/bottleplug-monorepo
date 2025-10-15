from django.test import TestCase
from django.conf import settings
from unittest.mock import patch, MagicMock
import json
from .auth_manager import FlutterwaveAuthManager
from .api_versioning import APIVersionManager
from .services import FlutterwaveService
from .error_handling import FlutterwaveErrorHandler


class FlutterwaveV4IntegrationTests(TestCase):
    """
    Comprehensive tests for Flutterwave v4 API integration
    """

    def setUp(self):
        """Set up test fixtures"""
        self.auth_manager = FlutterwaveAuthManager()
        self.version_manager = APIVersionManager()
        self.error_handler = FlutterwaveErrorHandler()
        self.flutterwave_service = FlutterwaveService()

        # Test credentials
        self.test_client_id = 'test-client-id'
        self.test_client_secret = 'test-client-secret'
        self.test_access_token = 'test-access-token'

    def test_v4_configuration(self):
        """Test that v4 configuration is properly set"""
        # Check API version
        self.assertEqual(settings.FLUTTERWAVE_API_VERSION, '2024-01-01')

        # Check base URLs
        self.assertEqual(settings.FLUTTERWAVE_SANDBOX_URL, 'https://developersandbox-api.flutterwave.com')
        self.assertEqual(settings.FLUTTERWAVE_PRODUCTION_URL, 'https://api.flutterwave.com')

        # Check OAuth endpoint
        self.assertEqual(settings.FLUTTERWAVE_OAUTH_TOKEN_URL, 'https://auth.flutterwave.com/oauth/token')

    @patch('requests.post')
    def test_oauth_token_generation(self, mock_post):
        """Test OAuth 2.0 token generation"""
        # Mock successful OAuth response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': self.test_access_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        # Test token generation
        auth_manager = FlutterwaveAuthManager(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )

        success = auth_manager.generate_access_token()

        # Assertions
        self.assertTrue(success)
        self.assertEqual(auth_manager.access_token, self.test_access_token)
        self.assertEqual(auth_manager.token_type, 'Bearer')

        # Check that the correct endpoint was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('https://auth.flutterwave.com/oauth/token', call_args[0])

    def test_v4_headers_generation(self):
        """Test v4 API headers generation"""
        auth_manager = FlutterwaveAuthManager(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        auth_manager.access_token = self.test_access_token
        auth_manager.token_type = 'Bearer'

        headers = auth_manager.get_v4_headers(
            include_idempotency=True,
            include_trace=True,
            scenario_key='test-scenario'
        )

        # Check required headers
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], f'Bearer {self.test_access_token}')
        self.assertIn('Content-Type', headers)
        self.assertIn('Flutterwave-Version', headers)
        self.assertEqual(headers['Flutterwave-Version'], '2024-01-01')
        self.assertIn('X-Idempotency-Key', headers)
        self.assertIn('X-Trace-Id', headers)
        self.assertIn('X-Scenario-Key', headers)
        self.assertEqual(headers['X-Scenario-Key'], 'test-scenario')

    def test_api_version_compatibility(self):
        """Test API version compatibility checks"""
        version_manager = APIVersionManager()

        # Test v4 features
        self.assertTrue(version_manager.supports_oauth())
        self.assertTrue(version_manager.supports_v4_headers())
        self.assertTrue(version_manager.supports_scenarios())

        # Test version info
        version_info = version_manager.get_version_info()
        self.assertEqual(version_info['version'], '2024-01-01')
        self.assertEqual(version_info['name'], 'v4 (Latest)')
        self.assertFalse(version_info['deprecated'])

    @patch('requests.post')
    def test_payment_creation_endpoint(self, mock_post):
        """Test payment creation uses correct v4 endpoint"""
        # Mock successful payment response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'message': 'Payment created successfully',
            'data': {
                'link': 'https://checkout.flutterwave.com/v3/hosted/pay/test-ref',
                'reference': 'test-ref'
            }
        }
        mock_response.headers = {'X-Idempotency-Cache-Hit': 'false'}
        mock_post.return_value = mock_response

        # Create a mock transaction
        from orders.models import Order
        from payments.models import Transaction

        # This would normally create a real transaction, but for testing we'll mock it
        mock_transaction = MagicMock()
        mock_transaction.reference = 'test-ref'
        mock_transaction.amount = 100.00
        mock_transaction.save = MagicMock()

        # Test payment creation
        service = FlutterwaveService()
        service.secret_key = 'test-secret'  # Enable real API calls

        with patch.object(service, '_get_headers') as mock_headers:
            mock_headers.return_value = {'Authorization': 'Bearer test-token'}
            result = service.create_payment_link(mock_transaction)

        # Check that the correct endpoint was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('/charges', call_args[0][0])  # v4 uses /charges endpoint

        # Check result
        self.assertTrue(result['success'])

    @patch('requests.get')
    def test_payment_verification_endpoint(self, mock_get):
        """Test payment verification uses correct v4 endpoint"""
        # Mock successful verification response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': {
                'status': 'successful',
                'amount': 100.00,
                'reference': 'test-ref'
            }
        }
        mock_get.return_value = mock_response

        service = FlutterwaveService()
        service.secret_key = 'test-secret'

        with patch.object(service, '_get_headers') as mock_headers:
            mock_headers.return_value = {'Authorization': 'Bearer test-token'}
            result = service.verify_payment('test-transaction-id')

        # Check that the correct endpoint was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('/charges/test-transaction-id', call_args[0][0])  # v4 uses /charges/{id}

        # Check result
        self.assertTrue(result['success'])


class FlutterwaveV4ErrorHandlingTests(TestCase):
    """
    Tests for v4 error handling
    """

    def setUp(self):
        self.error_handler = FlutterwaveErrorHandler()

    def test_v4_error_response_handling(self):
        """Test handling of v4 error responses"""
        # Mock v4 error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'status': 'error',
            'message': 'Invalid payment data',
            'code': '10400',
            'data': None
        }

        success, result = self.error_handler.handle_response(mock_response, "Payment creation")

        self.assertFalse(success)
        self.assertIn('error', result)
        self.assertEqual(result['error']['error_code'], '10400')
        self.assertIn('Invalid payment data', result['error']['error_message'])

    def test_oauth_error_handling(self):
        """Test OAuth-specific error handling"""
        # Mock OAuth error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': 'invalid_client',
            'error_description': 'Client authentication failed'
        }

        success, result = self.error_handler.handle_response(mock_response, "OAuth token generation")

        self.assertFalse(success)
        self.assertIn('error', result)
        self.assertIn('Client authentication failed', result['error']['error_message'])


class FlutterwaveV4ScenarioTests(TestCase):
    """
    Tests for v4 scenario-based testing
    """

    def test_scenario_header_inclusion(self):
        """Test that scenario headers are properly included"""
        auth_manager = FlutterwaveAuthManager()
        auth_manager.access_token = 'test-token'

        headers = auth_manager.get_v4_headers(scenario_key='successful_payment')

        self.assertIn('X-Scenario-Key', headers)
        self.assertEqual(headers['X-Scenario-Key'], 'successful_payment')

    def test_idempotency_key_generation(self):
        """Test idempotency key generation and usage"""
        auth_manager = FlutterwaveAuthManager()
        auth_manager.access_token = 'test-token'

        # Test auto-generated idempotency key
        headers1 = auth_manager.get_v4_headers(include_idempotency=True)
        headers2 = auth_manager.get_v4_headers(include_idempotency=True)

        self.assertIn('X-Idempotency-Key', headers1)
        self.assertIn('X-Idempotency-Key', headers2)
        self.assertNotEqual(headers1['X-Idempotency-Key'], headers2['X-Idempotency-Key'])

        # Test custom idempotency key
        custom_key = 'custom-idempotency-key'
        headers3 = auth_manager.get_v4_headers(
            include_idempotency=True,
            custom_idempotency_key=custom_key
        )

        self.assertEqual(headers3['X-Idempotency-Key'], custom_key)
