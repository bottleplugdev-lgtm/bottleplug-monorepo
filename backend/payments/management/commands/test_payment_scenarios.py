from django.core.management.base import BaseCommand
from payments.services import FlutterwaveService
from payments.testing_scenarios import FlutterwaveTestScenarios
import requests
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave payment scenarios with different test cases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            choices=['sandbox', 'production'],
            default='sandbox',
            help='Environment to test (sandbox or production)',
        )
        parser.add_argument(
            '--payment-type',
            choices=['card', 'mobile_money', 'transfer'],
            default='card',
            help='Payment type to test',
        )
        parser.add_argument(
            '--scenario',
            default=None,
            help='Specific scenario to test (e.g., auth_avs, auth_3ds)',
        )
        parser.add_argument(
            '--issuer',
            default=None,
            help='Card issuer response (e.g., approved, insufficient_funds)',
        )
        parser.add_argument(
            '--amount',
            type=int,
            default=1000,
            help='Payment amount in cents (default: 1000)',
        )
        parser.add_argument(
            '--list-scenarios',
            action='store_true',
            help='List all available scenarios for the payment type',
        )

    def handle(self, *args, **options):
        environment = options['environment']
        payment_type = options['payment_type']
        scenario = options['scenario']
        issuer = options['issuer']
        amount = options['amount']
        list_scenarios = options['list_scenarios']
        
        self.stdout.write(f'Testing {payment_type.upper()} Scenarios - Environment: {environment.upper()}')
        self.stdout.write(f'Amount: UGX {amount:,}')
        
        # Initialize Flutterwave service
        flutterwave_service = FlutterwaveService()
        
        # Override environment for testing
        if environment == 'production':
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/f4bexperience'
        else:
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/developersandbox'
        
        self.stdout.write(f'Base URL: {flutterwave_service.base_url}')
        
        # List scenarios if requested
        if list_scenarios:
            self._list_scenarios(payment_type)
            return
        
        # Test specific scenario or run comprehensive tests
        if scenario:
            self._test_specific_scenario(
                flutterwave_service, payment_type, scenario, issuer, amount
            )
        else:
            self._test_comprehensive_scenarios(
                flutterwave_service, payment_type, amount
            )
    
    def _list_scenarios(self, payment_type):
        """List all available scenarios for the payment type"""
        self.stdout.write(f'\n=== Available {payment_type.upper()} Scenarios ===')
        
        if payment_type == 'card':
            self.stdout.write('\nCard Authentication Scenarios:')
            for key, description in FlutterwaveTestScenarios.get_card_scenarios().items():
                self.stdout.write(f'  {key}: {description}')
            
            self.stdout.write('\nCard Issuer Responses:')
            for key, description in FlutterwaveTestScenarios.get_card_issuer_responses().items():
                self.stdout.write(f'  {key}: {description}')
                
        elif payment_type == 'mobile_money':
            self.stdout.write('\nMobile Money Scenarios:')
            for key, description in FlutterwaveTestScenarios.get_mobile_money_scenarios().items():
                self.stdout.write(f'  {key}: {description}')
                
        elif payment_type == 'transfer':
            self.stdout.write('\nTransfer Scenarios:')
            for key, description in FlutterwaveTestScenarios.get_transfer_scenarios().items():
                self.stdout.write(f'  {key}: {description}')
    
    def _test_specific_scenario(self, flutterwave_service, payment_type, scenario, issuer, amount):
        """Test a specific scenario"""
        self.stdout.write(f'\n=== Testing Specific Scenario ===')
        self.stdout.write(f'Payment Type: {payment_type}')
        self.stdout.write(f'Scenario: {scenario}')
        if issuer:
            self.stdout.write(f'Issuer: {issuer}')
        
        # Generate scenario key
        try:
            if payment_type == 'card':
                if not issuer:
                    issuer = 'approved'  # Default issuer
                scenario_key = FlutterwaveTestScenarios.generate_card_scenario_key(scenario, issuer)
            elif payment_type == 'mobile_money':
                scenario_key = FlutterwaveTestScenarios.generate_mobile_money_scenario_key(scenario)
            elif payment_type == 'transfer':
                scenario_key = FlutterwaveTestScenarios.generate_transfer_scenario_key(scenario)
            else:
                raise ValueError(f"Unsupported payment type: {payment_type}")
            
            self.stdout.write(f'Scenario Key: {scenario_key}')
            
        except ValueError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Invalid scenario: {e}')
            )
            return
        
        # Test the scenario
        self._make_test_request(flutterwave_service, payment_type, scenario_key, amount)
    
    def _test_comprehensive_scenarios(self, flutterwave_service, payment_type, amount):
        """Test comprehensive scenarios for the payment type"""
        self.stdout.write(f'\n=== Testing Comprehensive {payment_type.upper()} Scenarios ===')
        
        # Get successful scenarios
        successful_scenarios = FlutterwaveTestScenarios.get_successful_scenarios()
        failure_scenarios = FlutterwaveTestScenarios.get_failure_scenarios()
        
        # Test successful scenarios
        self.stdout.write('\n--- Testing Successful Scenarios ---')
        if payment_type in successful_scenarios:
            scenario_info = successful_scenarios[payment_type]
            if payment_type == 'card':
                scenario_key = FlutterwaveTestScenarios.generate_card_scenario_key(
                    scenario_info['scenario'], scenario_info['issuer']
                )
            elif payment_type == 'mobile_money':
                scenario_key = FlutterwaveTestScenarios.generate_mobile_money_scenario_key(
                    scenario_info['scenario']
                )
            elif payment_type == 'transfer':
                scenario_key = FlutterwaveTestScenarios.generate_transfer_scenario_key(
                    scenario_info['scenario']
                )
            
            self.stdout.write(f'Testing: {scenario_info["description"]}')
            self._make_test_request(flutterwave_service, payment_type, scenario_key, amount)
        
        # Test failure scenarios
        self.stdout.write('\n--- Testing Failure Scenarios ---')
        if payment_type in failure_scenarios:
            for i, scenario_info in enumerate(failure_scenarios[payment_type][:3]):  # Test first 3
                self.stdout.write(f'\n{i+1}. Testing: {scenario_info["description"]}')
                
                if payment_type == 'card':
                    scenario_key = FlutterwaveTestScenarios.generate_card_scenario_key(
                        scenario_info['scenario'], scenario_info['issuer']
                    )
                elif payment_type == 'mobile_money':
                    scenario_key = FlutterwaveTestScenarios.generate_mobile_money_scenario_key(
                        scenario_info['scenario']
                    )
                elif payment_type == 'transfer':
                    scenario_key = FlutterwaveTestScenarios.generate_transfer_scenario_key(
                        scenario_info['scenario']
                    )
                
                self._make_test_request(flutterwave_service, payment_type, scenario_key, amount)
    
    def _make_test_request(self, flutterwave_service, payment_type, scenario_key, amount):
        """Make a test request with the given scenario"""
        # Create test payload
        payload = {
            'tx_ref': f'test_{payment_type}_{int(time.time())}',
            'amount': str(amount),
            'currency': 'UGX',
            'redirect_url': 'https://example.com/return',
            'customer': {
                'email': 'test@example.com',
                'name': 'Test Customer',
                'phone_number': '+256700000000'
            },
            'customizations': {
                'title': f'{payment_type.title()} Test',
                'description': f'Testing {payment_type} with scenario: {scenario_key}',
                'logo': 'https://example.com/logo.png'
            },
            'meta': {
                'test_scenario': True,
                'payment_type': payment_type,
                'scenario_key': scenario_key
            }
        }
        
        # Add payment-specific options
        if payment_type == 'card':
            payload['payment_options'] = 'card'
        elif payment_type == 'mobile_money':
            payload['payment_options'] = 'mobile_money'
        elif payment_type == 'transfer':
            # For transfers, we need different endpoint and payload structure
            payload = {
                'account_bank': '044',
                'account_number': '0690000032',
                'amount': amount,
                'currency': 'UGX',
                'debit_currency': 'UGX',
                'reference': f'test_transfer_{int(time.time())}',
                'narration': f'Test transfer with scenario: {scenario_key}',
                'meta': {
                    'test_scenario': True,
                    'payment_type': payment_type,
                    'scenario_key': scenario_key
                }
            }
        
        # Get headers with scenario key
        headers = flutterwave_service._get_headers(
            include_idempotency=True,
            include_trace=True,
            scenario_key=scenario_key
        )
        
        self.stdout.write('Headers:')
        for key, value in headers.items():
            if key == 'Authorization':
                self.stdout.write(f'  {key}: Bearer {value[:20]}...')
            else:
                self.stdout.write(f'  {key}: {value}')
        
        # Make API request
        try:
            if payment_type == 'transfer':
                url = f"{flutterwave_service.base_url}/transfers"
            else:
                url = f"{flutterwave_service.base_url}/payments"
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            self.stdout.write(f'\nResponse Status: {response.status_code}')
            
            # Check for idempotency cache hit
            cache_hit = response.headers.get('X-Idempotency-Cache-Hit', 'false').lower() == 'true'
            self.stdout.write(f'Cache Hit: {cache_hit}')
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(
                    self.style.SUCCESS('✅ Request successful')
                )
                
                # Show response details
                if 'data' in data:
                    response_data = data['data']
                    if payment_type == 'transfer':
                        self.stdout.write(f'  Transfer ID: {response_data.get("id", "N/A")}')
                        self.stdout.write(f'  Reference: {response_data.get("reference", "N/A")}')
                        self.stdout.write(f'  Status: {response_data.get("status", "N/A")}')
                    else:
                        self.stdout.write(f'  Reference: {response_data.get("reference", "N/A")}')
                        self.stdout.write(f'  Payment URL: {response_data.get("link", "N/A")}')
                        self.stdout.write(f'  Status: {response_data.get("status", "N/A")}')
                
                self.stdout.write(f'  Response Status: {data.get("status", "N/A")}')
                self.stdout.write(f'  Message: {data.get("message", "N/A")}')
                
            elif response.status_code == 400:
                # Expected for failure scenarios
                data = response.json()
                self.stdout.write(
                    self.style.WARNING('⚠️ Expected failure (400)')
                )
                self.stdout.write(f'  Error: {data.get("message", "N/A")}')
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Request failed: {response.status_code}')
                )
                self.stdout.write(f'Response: {response.text}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error making request: {e}')
            )
        
        self.stdout.write('')  # Empty line for readability 