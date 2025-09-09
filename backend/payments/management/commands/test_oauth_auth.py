from django.core.management.base import BaseCommand
from payments.auth_manager import FlutterwaveAuthManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test OAuth 2.0 authentication with Flutterwave'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed token information',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write('Testing Flutterwave OAuth 2.0 authentication...')
        
        # Initialize auth manager
        auth_manager = FlutterwaveAuthManager()
        
        # Check if OAuth is configured
        if not auth_manager.is_oauth_configured():
            self.stdout.write(
                self.style.WARNING('❌ OAuth 2.0 credentials not configured')
            )
            self.stdout.write('Please set FLW_CLIENT_ID and FLW_CLIENT_SECRET environment variables')
            return
        
        self.stdout.write('✅ OAuth 2.0 credentials found')
        
        # Test token generation
        self.stdout.write('Generating access token...')
        if auth_manager.generate_access_token():
            self.stdout.write(
                self.style.SUCCESS('✅ Access token generated successfully')
            )
            
            # Get token info
            token_info = auth_manager.get_token_info()
            
            if verbose:
                self.stdout.write('\nToken Information:')
                self.stdout.write(f'  Token Type: {token_info["token_type"]}')
                self.stdout.write(f'  Expires At: {token_info["expires_at"]}')
                self.stdout.write(f'  Time Until Expiry: {token_info["time_until_expiry"]:.0f} seconds')
            
            # Test headers generation
            headers = auth_manager.get_auth_headers()
            if 'Authorization' in headers and headers['Authorization'].startswith('Bearer '):
                self.stdout.write(
                    self.style.SUCCESS('✅ Authorization headers generated successfully')
                )
                
                if verbose:
                    self.stdout.write(f'  Authorization: {headers["Authorization"][:50]}...')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Failed to generate authorization headers')
                )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Failed to generate access token')
            )
            self.stdout.write('Please check your OAuth credentials and network connection')
        
        self.stdout.write('\nOAuth 2.0 authentication test completed') 