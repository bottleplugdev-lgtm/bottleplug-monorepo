from django.core.management.base import BaseCommand
from payments.card_payments import FlutterwaveCardPayments
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave Card Payments implementation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-step',
            choices=['customer', 'payment_method', 'charge', 'authorize', 'verify', 'complete'],
            help='Test specific step of the card payment flow',
        )
        parser.add_argument(
            '--test-auth-model',
            choices=['pin', 'otp', 'avs', '3ds'],
            help='Test specific authorization model',
        )
        parser.add_argument(
            '--test-recurring',
            action='store_true',
            help='Test recurring card payment flow',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=1000.0,
            help='Payment amount (default: 1000.0)',
        )
        parser.add_argument(
            '--scenario',
            type=str,
            help='Test scenario key (e.g., scenario:auth_3ds&issuer:approved)',
        )

    def handle(self, *args, **options):
        test_step = options['test_step']
        test_auth_model = options['test_auth_model']
        test_recurring = options['test_recurring']
        amount = options['amount']
        scenario = options['scenario']
        
        self.stdout.write('Testing Flutterwave Card Payments')
        
        # Initialize card payments
        card_payments = FlutterwaveCardPayments()
        
        if test_step:
            self._test_specific_step(card_payments, test_step, amount)
        elif test_auth_model:
            self._test_auth_model(card_payments, test_auth_model, amount, scenario)
        elif test_recurring:
            self._test_recurring_payment(card_payments, amount)
        else:
            # Test complete flow
            self._test_complete_flow(card_payments, amount)
    
    def _test_specific_step(self, card_payments, step, amount):
        """Test a specific step of the card payment flow"""
        self.stdout.write(f'\n=== Testing Step: {step.upper()} ===')
        
        if step == 'customer':
            self._test_customer_creation(card_payments)
        elif step == 'payment_method':
            self._test_payment_method_creation(card_payments)
        elif step == 'charge':
            self._test_charge_initiation(card_payments, amount)
        elif step == 'authorize':
            self._test_charge_authorization(card_payments)
        elif step == 'verify':
            self._test_payment_verification(card_payments)
        elif step == 'complete':
            self._test_complete_flow(card_payments, amount)
    
    def _test_customer_creation(self, card_payments):
        """Test customer creation"""
        self.stdout.write('\n--- Testing Customer Creation ---')
        
        customer_data = {
            'email': f'card_test_{int(time.time())}@example.com',
            'name': {
                'first': 'Card',
                'last': 'User'
            },
            'phone': {
                'country_code': '256',
                'number': '700000000'
            }
        }
        
        result = card_payments.create_customer(customer_data)
        
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
    
    def _test_payment_method_creation(self, card_payments):
        """Test card payment method creation"""
        self.stdout.write('\n--- Testing Card Payment Method Creation ---')
        
        # First create a customer
        customer_result = self._test_customer_creation(card_payments)
        if not customer_result['success']:
            return customer_result
        
        card_data = {
            'card_number': '4084084084084081',  # Valid test card
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '30',
            'cardholder_name': 'Card User'
        }
        
        result = card_payments.create_card_payment_method(card_data, customer_result['customer_id'])
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Card payment method created successfully')
            )
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Card Network: {result["payment_method_data"]["card"]["network"]}')
            self.stdout.write(f'Last 4: {result["payment_method_data"]["card"]["last4"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Card payment method creation failed: {result["error"]}')
            )
        
        return result
    
    def _test_charge_initiation(self, card_payments, amount):
        """Test card charge initiation"""
        self.stdout.write('\n--- Testing Card Charge Initiation ---')
        
        # First create a customer and payment method
        customer_result = self._test_customer_creation(card_payments)
        if not customer_result['success']:
            return customer_result
        
        payment_method_result = card_payments.create_card_payment_method({
            'card_number': '4084084084084081',
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '30',
            'cardholder_name': 'Card User'
        }, customer_result['customer_id'])
        
        if not payment_method_result['success']:
            return payment_method_result
        
        # Initiate charge
        charge_data = {
            'reference': f'card_charge_{int(time.time())}',
            'currency': 'USD',
            'customer_id': customer_result['customer_id'],
            'payment_method_id': payment_method_result['payment_method_id'],
            'amount': amount,
            'redirect_url': 'https://example.com/return',
            'meta': {
                'test_card_payment': True,
                'amount': amount
            }
        }
        
        result = card_payments.initiate_card_charge(charge_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Card charge initiated successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            
            if result.get('next_action'):
                self.stdout.write(f'Next Action: {result["next_action"]["type"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Card charge initiation failed: {result["error"]}')
            )
        
        return result
    
    def _test_charge_authorization(self, card_payments):
        """Test card charge authorization"""
        self.stdout.write('\n--- Testing Card Charge Authorization ---')
        
        # This would typically be called after charge initiation
        # For testing, we'll simulate with a mock charge ID
        charge_id = 'chg_test_123'
        
        authorization_data = {
            'type': 'pin',
            'pin': {
                'nonce': 'test_nonce',
                'encrypted_pin': 'test_encrypted_pin'
            }
        }
        
        result = card_payments.authorize_card_payment(charge_id, authorization_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Card charge authorized successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Card charge authorization failed: {result["error"]}')
            )
        
        return result
    
    def _test_payment_verification(self, card_payments):
        """Test card payment verification"""
        self.stdout.write('\n--- Testing Card Payment Verification ---')
        
        # This would typically be called with a real charge ID
        # For testing, we'll simulate with a mock charge ID
        charge_id = 'chg_test_123'
        
        result = card_payments.verify_card_payment(charge_id)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Card payment verified successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            self.stdout.write(f'Amount: {result["amount"]}')
            self.stdout.write(f'Currency: {result["currency"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Card payment verification failed: {result["error"]}')
            )
        
        return result
    
    def _test_auth_model(self, card_payments, auth_model, amount, scenario=None):
        """Test specific authorization model"""
        self.stdout.write(f'\n=== Testing {auth_model.upper()} Authorization Model ===')
        
        payment_data = {
            'customer_data': {
                'email': f'{auth_model}_test_{int(time.time())}@example.com',
                'name': {
                    'first': auth_model.title(),
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000000'
                }
            },
            'card_data': {
                'card_number': '4084084084084081',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '30',
                'cardholder_name': f'{auth_model.title()} User'
            },
            'charge_data': {
                'reference': f'{auth_model}_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'auth_model': auth_model,
                    'test_auth_model': True
                }
            }
        }
        
        # Add scenario key if provided
        if scenario:
            payment_data['charge_data']['scenario'] = scenario
        
        # Add authorization data based on auth model
        if auth_model == 'pin':
            payment_data['authorization_data'] = {
                'type': 'pin',
                'pin': {
                    'nonce': 'test_nonce_123',
                    'encrypted_pin': 'test_encrypted_pin_456'
                }
            }
        elif auth_model == 'otp':
            payment_data['authorization_data'] = {
                'type': 'otp',
                'otp': {
                    'code': '123456'
                }
            }
        elif auth_model == 'avs':
            payment_data['authorization_data'] = {
                'type': 'avs',
                'avs': {
                    'address': {
                        'city': 'Gotham',
                        'country': 'US',
                        'line1': '221B Baker Street',
                        'line2': 'Coker Estate',
                        'postal_code': '94105',
                        'state': 'Colorado'
                    }
                }
            }
        
        result = card_payments.complete_card_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {auth_model.upper()} authorization model completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ {auth_model.upper()} authorization model failed: {result["error"]}')
            )
        
        return result
    
    def _test_recurring_payment(self, card_payments, amount):
        """Test recurring card payment flow"""
        self.stdout.write('\n=== Testing Recurring Card Payment Flow ===')
        
        payment_data = {
            'customer_data': {
                'email': f'recurring_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'Recurring',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000000'
                }
            },
            'card_data': {
                'card_number': '4084084084084081',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '30',
                'cardholder_name': 'Recurring User'
            },
            'charge_data': {
                'reference': f'recurring_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'recurring': True,
                'meta': {
                    'payment_type': 'recurring',
                    'test_recurring_payment': True
                }
            }
        }
        
        result = card_payments.complete_card_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Recurring card payment flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Recurring card payment flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_complete_flow(self, card_payments, amount):
        """Test complete card payment flow"""
        self.stdout.write('\n--- Testing Complete Card Payment Flow ---')
        
        payment_data = {
            'customer_data': {
                'email': f'complete_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'Complete',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000000'
                }
            },
            'card_data': {
                'card_number': '4084084084084081',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '30',
                'cardholder_name': 'Complete User'
            },
            'charge_data': {
                'reference': f'complete_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'test_complete_flow': True
                }
            }
        }
        
        result = card_payments.complete_card_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Complete card payment flow successful')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Complete card payment flow failed: {result["error"]}')
            )
        
        return result 