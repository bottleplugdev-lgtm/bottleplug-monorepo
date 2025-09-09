from django.core.management.base import BaseCommand
from payments.services import FlutterwaveService
import requests
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test idempotency functionality with duplicate requests'

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

    def handle(self, *args, **options):
        environment = options['environment']
        amount = options['amount']
        
        self.stdout.write(f'Testing Idempotency - Environment: {environment.upper()}')
        self.stdout.write(f'Amount: UGX {amount:,}')
        
        # Initialize Flutterwave service
        flutterwave_service = FlutterwaveService()
        
        # Override environment for testing
        if environment == 'production':
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/f4bexperience'
        else:
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/developersandbox'
        
        self.stdout.write(f'Base URL: {flutterwave_service.base_url}')
        
        # Generate a unique idempotency key for testing
        import uuid
        test_idempotency_key = f"test_idempotency_{str(uuid.uuid4())}"
        
        self.stdout.write(f'Test Idempotency Key: {test_idempotency_key}')
        
        # Test payload
        payload = {
            'tx_ref': f'test_idempotency_{int(time.time())}',
            'amount': str(amount),
            'currency': 'UGX',
            'redirect_url': 'https://example.com/return',
            'customer': {
                'email': 'test@example.com',
                'name': 'Test Customer',
                'phone_number': '+256700000000'
            },
            'customizations': {
                'title': 'Idempotency Test',
                'description': 'Testing idempotency with duplicate requests',
                'logo': 'https://example.com/logo.png'
            },
            'meta': {
                'test_idempotency': True,
                'environment': environment
            },
            'payment_options': 'card,mobile_money,mpesa,bank transfer,cash'
        }
        
        # First request
        self.stdout.write('\n=== First Request ===')
        headers1 = flutterwave_service._get_headers(
            include_idempotency=True,
            include_trace=True,
            custom_idempotency_key=test_idempotency_key
        )
        
        self.stdout.write('Headers (First Request):')
        for key, value in headers1.items():
            if key == 'Authorization':
                self.stdout.write(f'  {key}: Bearer {value[:20]}...')
            else:
                self.stdout.write(f'  {key}: {value}')
        
        try:
            url = f"{flutterwave_service.base_url}/payments"
            response1 = requests.post(url, headers=headers1, json=payload, timeout=30)
            
            self.stdout.write(f'\nFirst Request Response: {response1.status_code}')
            cache_hit1 = response1.headers.get('X-Idempotency-Cache-Hit', 'false').lower() == 'true'
            self.stdout.write(f'Cache Hit: {cache_hit1}')
            
            if response1.status_code == 200:
                data1 = response1.json()
                self.stdout.write(
                    self.style.SUCCESS('✅ First request successful')
                )
                if 'data' in data1:
                    self.stdout.write(f'  Reference: {data1["data"].get("reference", "N/A")}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ First request failed: {response1.text}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error in first request: {e}')
            )
        
        # Wait a moment
        time.sleep(2)
        
        # Second request with same idempotency key
        self.stdout.write('\n=== Second Request (Same Idempotency Key) ===')
        headers2 = flutterwave_service._get_headers(
            include_idempotency=True,
            include_trace=True,
            custom_idempotency_key=test_idempotency_key  # Same key
        )
        
        self.stdout.write('Headers (Second Request):')
        for key, value in headers2.items():
            if key == 'Authorization':
                self.stdout.write(f'  {key}: Bearer {value[:20]}...')
            else:
                self.stdout.write(f'  {key}: {value}')
        
        try:
            response2 = requests.post(url, headers=headers2, json=payload, timeout=30)
            
            self.stdout.write(f'\nSecond Request Response: {response2.status_code}')
            cache_hit2 = response2.headers.get('X-Idempotency-Cache-Hit', 'false').lower() == 'true'
            self.stdout.write(f'Cache Hit: {cache_hit2}')
            
            if response2.status_code == 200:
                data2 = response2.json()
                self.stdout.write(
                    self.style.SUCCESS('✅ Second request successful')
                )
                if 'data' in data2:
                    self.stdout.write(f'  Reference: {data2["data"].get("reference", "N/A")}')
                
                # Check if responses are identical (idempotency working)
                if data1.get('data', {}).get('reference') == data2.get('data', {}).get('reference'):
                    self.stdout.write(
                        self.style.SUCCESS('✅ Idempotency working: Same reference returned')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Idempotency check: Different references returned')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Second request failed: {response2.text}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error in second request: {e}')
            )
        
        # Third request with different idempotency key
        self.stdout.write('\n=== Third Request (Different Idempotency Key) ===')
        different_idempotency_key = f"test_idempotency_{str(uuid.uuid4())}"
        self.stdout.write(f'Different Idempotency Key: {different_idempotency_key}')
        
        headers3 = flutterwave_service._get_headers(
            include_idempotency=True,
            include_trace=True,
            custom_idempotency_key=different_idempotency_key
        )
        
        try:
            response3 = requests.post(url, headers=headers3, json=payload, timeout=30)
            
            self.stdout.write(f'\nThird Request Response: {response3.status_code}')
            cache_hit3 = response3.headers.get('X-Idempotency-Cache-Hit', 'false').lower() == 'true'
            self.stdout.write(f'Cache Hit: {cache_hit3}')
            
            if response3.status_code == 200:
                data3 = response3.json()
                self.stdout.write(
                    self.style.SUCCESS('✅ Third request successful')
                )
                if 'data' in data3:
                    self.stdout.write(f'  Reference: {data3["data"].get("reference", "N/A")}')
                
                # Check if this is a new request (different reference)
                ref1 = data1.get('data', {}).get('reference')
                ref3 = data3.get('data', {}).get('reference')
                if ref1 != ref3:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Different idempotency key: New request processed')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Different idempotency key: Same reference returned')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Third request failed: {response3.text}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error in third request: {e}')
            )
        
        self.stdout.write('\n=== Idempotency Test Summary ===')
        self.stdout.write(f'First Request Cache Hit: {cache_hit1}')
        self.stdout.write(f'Second Request Cache Hit: {cache_hit2}')
        self.stdout.write(f'Third Request Cache Hit: {cache_hit3}')
        
        if cache_hit2:
            self.stdout.write(
                self.style.SUCCESS('✅ Idempotency working correctly: Second request returned cached response')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Idempotency check: Second request did not return cached response')
            )
        
        self.stdout.write('\nIdempotency test completed') 