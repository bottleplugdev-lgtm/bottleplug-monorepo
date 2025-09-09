from django.core.management.base import BaseCommand
from payments.mobile_money import FlutterwaveMobileMoney
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave Mobile Money implementation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-step',
            choices=['customer', 'payment_method', 'charge', 'verify', 'complete'],
            help='Test specific step of the mobile money payment flow',
        )
        parser.add_argument(
            '--test-country',
            type=str,
            default='GH',
            help='Country code to test (default: GH for Ghana)',
        )
        parser.add_argument(
            '--test-network',
            type=str,
            default='MTN',
            help='Mobile money network to test (default: MTN)',
        )
        parser.add_argument(
            '--test-flow',
            choices=['push_notification', 'redirect'],
            help='Test specific flow type',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=100.0,
            help='Payment amount (default: 100.0)',
        )
        parser.add_argument(
            '--scenario',
            type=str,
            help='Test scenario key (e.g., scenario:auth_redirect)',
        )
        parser.add_argument(
            '--list-countries',
            action='store_true',
            help='List all supported countries and networks',
        )

    def handle(self, *args, **options):
        test_step = options['test_step']
        test_country = options['test_country']
        test_network = options['test_network']
        test_flow = options['test_flow']
        amount = options['amount']
        scenario = options['scenario']
        list_countries = options['list_countries']
        
        self.stdout.write('Testing Flutterwave Mobile Money')
        
        # Initialize mobile money
        mobile_money = FlutterwaveMobileMoney()
        
        if list_countries:
            self._list_supported_countries(mobile_money)
        elif test_step:
            self._test_specific_step(mobile_money, test_step, test_country, test_network, amount)
        elif test_flow:
            self._test_specific_flow(mobile_money, test_flow, test_country, test_network, amount, scenario)
        else:
            # Test complete flow
            self._test_complete_flow(mobile_money, test_country, test_network, amount, scenario)
    
    def _list_supported_countries(self, mobile_money):
        """List all supported countries and networks"""
        self.stdout.write('\n=== Supported Countries and Networks ===')
        
        result = mobile_money.get_supported_countries()
        
        if result['success']:
            self.stdout.write(f'Total Countries: {result["total_countries"]}')
            self.stdout.write('\n--- Countries by Region ---')
            
            for region, countries in result['regions'].items():
                self.stdout.write(f'\n{region}:')
                for country_code in countries:
                    country_info = result['supported_countries'][country_code]
                    networks = ', '.join(country_info['networks'])
                    self.stdout.write(f'  {country_code} ({country_info["currency"]}): {networks}')
        else:
            self.stdout.write(
                self.style.ERROR('❌ Failed to get supported countries')
            )
    
    def _test_specific_step(self, mobile_money, step, country, network, amount):
        """Test a specific step of the mobile money payment flow"""
        self.stdout.write(f'\n=== Testing Step: {step.upper()} ===')
        
        if step == 'customer':
            self._test_customer_creation(mobile_money)
        elif step == 'payment_method':
            self._test_payment_method_creation(mobile_money, country, network)
        elif step == 'charge':
            self._test_charge_initiation(mobile_money, country, network, amount)
        elif step == 'verify':
            self._test_payment_verification(mobile_money)
        elif step == 'complete':
            self._test_complete_flow(mobile_money, country, network, amount)
    
    def _test_customer_creation(self, mobile_money):
        """Test customer creation"""
        self.stdout.write('\n--- Testing Customer Creation ---')
        
        customer_data = {
            'email': f'mobile_test_{int(time.time())}@example.com',
            'name': {
                'first': 'Mobile',
                'last': 'User'
            },
            'phone': {
                'country_code': '233',
                'number': '9012345678'
            }
        }
        
        result = mobile_money.create_customer(customer_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Customer created successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Email: {result["customer_data"]["email"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Customer creation failed: {result["error"]}')
            )
        
        return result
    
    def _test_payment_method_creation(self, mobile_money, country, network):
        """Test mobile money payment method creation"""
        self.stdout.write('\n--- Testing Mobile Money Payment Method Creation ---')
        
        # First create a customer
        customer_result = self._test_customer_creation(mobile_money)
        if not customer_result['success']:
            return customer_result
        
        mobile_money_data = {
            'country_code': country,
            'network': network,
            'phone_number': '784794196'  # Uganda MTN number
        }
        
        result = mobile_money.create_mobile_money_payment_method(mobile_money_data, customer_result['customer_id'])
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Mobile money payment method created successfully')
            )
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Network: {result["payment_method_data"]["mobile_money"]["network"]}')
            self.stdout.write(f'Country: {result["payment_method_data"]["mobile_money"]["country_code"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Mobile money payment method creation failed: {result["error"]}')
            )
        
        return result
    
    def _test_charge_initiation(self, mobile_money, country, network, amount):
        """Test mobile money charge initiation"""
        self.stdout.write('\n--- Testing Mobile Money Charge Initiation ---')
        
        # First create a customer and payment method
        customer_result = self._test_customer_creation(mobile_money)
        if not customer_result['success']:
            return customer_result
        
        payment_method_result = mobile_money.create_mobile_money_payment_method({
            'country_code': country,
            'network': network,
            'phone_number': '784794196'  # Uganda MTN number
        }, customer_result['customer_id'])
        
        if not payment_method_result['success']:
            return payment_method_result
        
        # Get country info for currency
        country_info = mobile_money.SUPPORTED_COUNTRIES.get(country, {})
        currency = country_info.get('currency', 'GHS')
        
        # Initiate charge
        charge_data = {
            'reference': f'mobile_charge_{int(time.time())}',
            'currency': currency,
            'customer_id': customer_result['customer_id'],
            'payment_method_id': payment_method_result['payment_method_id'],
            'amount': amount,
            'redirect_url': 'https://example.com/return',
            'meta': {
                'test_mobile_money': True,
                'amount': amount
            }
        }
        
        result = mobile_money.initiate_mobile_money_charge(charge_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Mobile money charge initiated successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            
            if result.get('next_action'):
                self.stdout.write(f'Next Action: {result["next_action"]["type"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Mobile money charge initiation failed: {result["error"]}')
            )
        
        return result
    
    def _test_payment_verification(self, mobile_money):
        """Test mobile money payment verification"""
        self.stdout.write('\n--- Testing Mobile Money Payment Verification ---')
        
        # This would typically be called with a real charge ID
        # For testing, we'll simulate with a mock charge ID
        charge_id = 'chg_test_123'
        
        result = mobile_money.verify_mobile_money_payment(charge_id)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Mobile money payment verified successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            self.stdout.write(f'Amount: {result["amount"]}')
            self.stdout.write(f'Currency: {result["currency"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Mobile money payment verification failed: {result["error"]}')
            )
        
        return result
    
    def _test_specific_flow(self, mobile_money, flow_type, country, network, amount, scenario=None):
        """Test specific flow type (push notification or redirect)"""
        self.stdout.write(f'\n=== Testing {flow_type.upper()} Flow ===')
        
        # Get country info for currency
        country_info = mobile_money.SUPPORTED_COUNTRIES.get(country, {})
        currency = country_info.get('currency', 'GHS')
        
        payment_data = {
            'customer_data': {
                'email': f'{flow_type}_test_{int(time.time())}@example.com',
                'name': {
                    'first': flow_type.title(),
                    'last': 'User'
                },
                'phone': {
                    'country_code': '233',
                    'number': '9012345678'
                }
            },
            'mobile_money_data': {
                'country_code': country,
                'network': network,
                'phone_number': '784794196'  # Uganda MTN number
            },
            'charge_data': {
                'reference': f'{flow_type}_payment_{int(time.time())}',
                'currency': currency,
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'flow_type': flow_type,
                    'test_flow': True
                }
            }
        }
        
        # Add scenario if provided
        if scenario:
            payment_data['scenario'] = scenario
        
        result = mobile_money.complete_mobile_money_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {flow_type.title()} flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            
            if 'note' in result:
                self.stdout.write(f'Instructions: {result["note"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ {flow_type.title()} flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_complete_flow(self, mobile_money, country, network, amount, scenario=None):
        """Test complete mobile money payment flow"""
        self.stdout.write('\n--- Testing Complete Mobile Money Payment Flow ---')
        
        # Get country info for currency
        country_info = mobile_money.SUPPORTED_COUNTRIES.get(country, {})
        currency = country_info.get('currency', 'GHS')
        
        payment_data = {
            'customer_data': {
                'email': f'complete_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'Complete',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '233',
                    'number': '9012345678'
                }
            },
            'mobile_money_data': {
                'country_code': country,
                'network': network,
                'phone_number': '784794196'  # Uganda MTN number
            },
            'charge_data': {
                'reference': f'complete_payment_{int(time.time())}',
                'currency': currency,
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'test_complete_flow': True
                }
            }
        }
        
        # Add scenario if provided
        if scenario:
            payment_data['scenario'] = scenario
        
        result = mobile_money.complete_mobile_money_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Complete mobile money payment flow successful')
            )
            if 'customer_id' in result:
                self.stdout.write(f'Customer ID: {result["customer_id"]}')
            if 'payment_method_id' in result:
                self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            if 'charge_id' in result:
                self.stdout.write(f'Charge ID: {result["charge_id"]}')
            if 'status' in result:
                self.stdout.write(f'Status: {result["status"]}')
            if 'note' in result:
                self.stdout.write(f'Instructions: {result["note"]}')
            if 'redirect_url' in result:
                self.stdout.write(f'Redirect URL: {result["redirect_url"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Complete mobile money payment flow failed: {result["error"]}')
            )
        
        return result 