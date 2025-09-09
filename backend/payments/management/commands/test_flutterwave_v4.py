from django.core.management.base import BaseCommand
from payments.services import FlutterwaveService
import requests
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave v4 API endpoints'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            choices=['sandbox', 'production'],
            default='sandbox',
            help='Environment to test (sandbox or production)',
        )
        parser.add_argument(
            '--endpoint',
            default='customers',
            help='API endpoint to test (default: customers)',
        )

    def handle(self, *args, **options):
        environment = options['environment']
        endpoint = options['endpoint']
        
        self.stdout.write(f'Testing Flutterwave v4 API - Environment: {environment.upper()}')
        
        # Initialize Flutterwave service
        flutterwave_service = FlutterwaveService()
        
        # Override environment for testing
        if environment == 'production':
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/f4bexperience'
        else:
            flutterwave_service.base_url = 'https://api.flutterwave.cloud/developersandbox'
        
        self.stdout.write(f'Base URL: {flutterwave_service.base_url}')
        
        # Test API endpoint
        try:
            url = f"{flutterwave_service.base_url}/{endpoint}?page=1"
            headers = flutterwave_service._get_headers(
                include_idempotency=False,  # GET requests don't need idempotency
                include_trace=True
            )
            
            self.stdout.write(f'Testing endpoint: {url}')
            self.stdout.write(f'Using authentication: {"OAuth 2.0" if flutterwave_service.auth_manager.is_oauth_configured() else "API Key"}')
            self.stdout.write('v4 API Headers:')
            for key, value in headers.items():
                if key == 'Authorization':
                    self.stdout.write(f'  {key}: Bearer {value[:20]}...')
                else:
                    self.stdout.write(f'  {key}: {value}')
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ API call successful (Status: {response.status_code})')
                )
                
                # Show response summary
                if 'data' in data:
                    self.stdout.write(f'Response contains {len(data["data"])} items')
                if 'meta' in data:
                    self.stdout.write(f'Total pages: {data["meta"].get("page_info", {}).get("total_pages", "N/A")}')
                
                self.stdout.write('API Response Structure:')
                for key in data.keys():
                    if isinstance(data[key], list):
                        self.stdout.write(f'  {key}: [{len(data[key])} items]')
                    elif isinstance(data[key], dict):
                        self.stdout.write(f'  {key}: {{...}}')
                    else:
                        self.stdout.write(f'  {key}: {data[key]}')
                        
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ API call failed (Status: {response.status_code})')
                )
                self.stdout.write(f'Response: {response.text}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error testing API: {e}')
            )
        
        self.stdout.write('\nFlutterwave v4 API test completed') 