from django.core.management.base import BaseCommand
from payments.services import FlutterwaveService
import requests
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test payment creation with Flutterwave v4 API headers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            choices=['sandbox', 'production'],
            default='sandbox',
            help='Environment to test (sandbox or production)',
        )
        parser.add_argument(
            '--amount',
            type=int,
            default=1000,
            help='Payment amount in cents (default: 1000)',
        )
        parser.add_argument(
            '--scenario',
            default=None,
            help='Scenario key for testing (optional)',
        )

    def handle(self, *args, **options):
        environment = options['environment']
        amount = options['amount']
        scenario_key = options['scenario']
        
        self.stdout.write(f'Testing Payment Creation - Environment: {environment.upper()}')
        self.stdout.write(f'Amount: UGX {amount:,}')
        if scenario_key:
            self.stdout.write(f'Scenario Key: {scenario_key}')
        
        # Initialize Flutterwave service
        flutterwave_service = FlutterwaveService()
        
        # Override environment for testing
        if environment == 'production':
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/f4bexperience'
        else:
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/developersandbox'
        
        self.stdout.write(f'Base URL: {flutterwave_service.base_url}')
        
        # Test payment creation
        try:
            # Create test payload
            payload = {
                'tx_ref': f'test_payment_{int(time.time())}',
                'amount': str(amount),
                'currency': 'UGX',
                'redirect_url': 'https://example.com/return',
                'customer': {
                    'email': 'test@example.com',
                    'name': 'Test Customer',
                    'phone_number': '+256700000000'
                },
                'customizations': {
                    'title': 'Test Payment',
                    'description': 'Test payment with v4 API headers',
                    'logo': 'https://example.com/logo.png'
                },
                'meta': {
                    'test_payment': True,
                    'environment': environment
                },
                'payment_options': 'card,mobile_money,mpesa,bank transfer,cash'
            }
            
            # Get v4 headers
            headers = flutterwave_service._get_headers(
                include_idempotency=True,
                include_trace=True,
                scenario_key=scenario_key
            )
            
            self.stdout.write('v4 API Headers:')
            for key, value in headers.items():
                if key == 'Authorization':
                    self.stdout.write(f'  {key}: Bearer {value[:20]}...')
                else:
                    self.stdout.write(f'  {key}: {value}')
            
            # Make API request
            url = f"{flutterwave_service.base_url}/payments"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Payment creation successful (Status: {response.status_code})')
                )
                
                self.stdout.write('Payment Response:')
                if 'data' in data:
                    payment_data = data['data']
                    self.stdout.write(f'  Reference: {payment_data.get("reference", "N/A")}')
                    self.stdout.write(f'  Payment URL: {payment_data.get("link", "N/A")}')
                    self.stdout.write(f'  Status: {payment_data.get("status", "N/A")}')
                
                self.stdout.write('Response Structure:')
                for key in data.keys():
                    if isinstance(data[key], dict):
                        self.stdout.write(f'  {key}: {{...}}')
                    elif isinstance(data[key], list):
                        self.stdout.write(f'  {key}: [{len(data[key])} items]')
                    else:
                        self.stdout.write(f'  {key}: {data[key]}')
                        
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Payment creation failed (Status: {response.status_code})')
                )
                self.stdout.write(f'Response: {response.text}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating payment: {e}')
            )
        
        self.stdout.write('\nPayment creation test completed') 