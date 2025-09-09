from django.core.management.base import BaseCommand
from payments.general_flow import FlutterwaveGeneralFlow
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave General Flow implementation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-step',
            choices=['customer', 'payment_method', 'charge', 'authorize', 'verify', 'complete'],
            help='Test specific step of the general flow',
        )
        parser.add_argument(
            '--test-card-payment',
            action='store_true',
            help='Test complete card payment flow',
        )
        parser.add_argument(
            '--test-mobile-money',
            action='store_true',
            help='Test complete mobile money payment flow',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=1000.0,
            help='Payment amount (default: 1000.0)',
        )

    def handle(self, *args, **options):
        test_step = options['test_step']
        test_card_payment = options['test_card_payment']
        test_mobile_money = options['test_mobile_money']
        amount = options['amount']
        
        self.stdout.write('Testing Flutterwave General Flow')
        
        # Initialize general flow
        general_flow = FlutterwaveGeneralFlow()
        
        if test_step:
            self._test_specific_step(general_flow, test_step, amount)
        elif test_card_payment:
            self._test_card_payment_flow(general_flow, amount)
        elif test_mobile_money:
            self._test_mobile_money_flow(general_flow, amount)
        else:
            # Test all steps
            self._test_all_steps(general_flow, amount)
    
    def _test_specific_step(self, general_flow, step, amount):
        """Test a specific step of the general flow"""
        self.stdout.write(f'\n=== Testing Step: {step.upper()} ===')
        
        if step == 'customer':
            self._test_customer_creation(general_flow)
        elif step == 'payment_method':
            self._test_payment_method_creation(general_flow)
        elif step == 'charge':
            self._test_charge_initiation(general_flow, amount)
        elif step == 'authorize':
            self._test_charge_authorization(general_flow)
        elif step == 'verify':
            self._test_payment_verification(general_flow)
        elif step == 'complete':
            self._test_complete_flow(general_flow, amount)
    
    def _test_customer_creation(self, general_flow):
        """Test customer creation"""
        self.stdout.write('\n--- Testing Customer Creation ---')
        
        customer_data = {
            'email': f'test_{int(time.time())}@example.com',
            'name': {
                'first': 'John',
                'last': 'Smith'
            },
            'phone': {
                'country_code': '256',
                'number': '700000000'
            }
        }
        
        result = general_flow.create_customer(customer_data)
        
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
    
    def _test_payment_method_creation(self, general_flow):
        """Test payment method creation"""
        self.stdout.write('\n--- Testing Payment Method Creation ---')
        
        # Test card payment method
        card_payment_method = {
            'type': 'card',
            'card': {
                'card_number': '4084084084084081',  # Valid test card
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '30',
                'cardholder_name': 'John Doe'
            }
        }
        
        result = general_flow.create_payment_method(card_payment_method)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Card payment method created successfully')
            )
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Card payment method creation failed: {result["error"]}')
            )
        
        # Test mobile money payment method
        mobile_money_payment_method = {
            'type': 'mobile_money',
            'mobile_money': {
                'country_code': '256',
                'network': 'MTN',
                'phone_number': '700000000'
            }
        }
        
        result = general_flow.create_payment_method(mobile_money_payment_method)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Mobile money payment method created successfully')
            )
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Mobile money payment method creation failed: {result["error"]}')
            )
    
    def _test_charge_initiation(self, general_flow, amount):
        """Test charge initiation"""
        self.stdout.write('\n--- Testing Charge Initiation ---')
        
        # First create a customer
        customer_result = self._test_customer_creation(general_flow)
        if not customer_result['success']:
            return customer_result
        
        # Create a payment method
        payment_method_result = general_flow.create_payment_method({
            'type': 'card',
            'card': {
                'card_number': '4084084084084081',  # Valid test card
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '30',
                'cardholder_name': 'John Doe'
            }
        })
        
        if not payment_method_result['success']:
            return payment_method_result
        
        # Initiate charge
        charge_data = {
            'reference': f'test_charge_{int(time.time())}',
            'currency': 'USD',
            'customer_id': customer_result['customer_id'],
            'payment_method_id': payment_method_result['payment_method_id'],
            'amount': amount,
            'redirect_url': 'https://example.com/return',
            'meta': {
                'test_payment': True,
                'amount': amount
            }
        }
        
        result = general_flow.initiate_charge(charge_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Charge initiated successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            
            if result.get('next_action'):
                self.stdout.write(f'Next Action: {result["next_action"]["type"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Charge initiation failed: {result["error"]}')
            )
        
        return result
    
    def _test_charge_authorization(self, general_flow):
        """Test charge authorization"""
        self.stdout.write('\n--- Testing Charge Authorization ---')
        
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
        
        result = general_flow.authorize_charge(charge_id, authorization_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Charge authorized successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Charge authorization failed: {result["error"]}')
            )
        
        return result
    
    def _test_payment_verification(self, general_flow):
        """Test payment verification"""
        self.stdout.write('\n--- Testing Payment Verification ---')
        
        # This would typically be called with a real charge ID
        # For testing, we'll simulate with a mock charge ID
        charge_id = 'chg_test_123'
        
        result = general_flow.verify_payment(charge_id)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Payment verified successfully')
            )
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            self.stdout.write(f'Amount: {result["amount"]}')
            self.stdout.write(f'Currency: {result["currency"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Payment verification failed: {result["error"]}')
            )
        
        return result
    
    def _test_complete_flow(self, general_flow, amount):
        """Test complete payment flow"""
        self.stdout.write('\n--- Testing Complete Payment Flow ---')
        
        payment_data = {
            'customer_data': {
                'email': f'test_{int(time.time())}@example.com',
                'name': {
                    'first': 'John',
                    'last': 'Doe'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000000'
                }
            },
            'payment_method_data': {
                'type': 'card',
                'card': {
                    'card_number': '4084084084084081',  # Valid test card
                    'cvv': '123',
                    'expiry_month': '12',
                    'expiry_year': '30',
                    'cardholder_name': 'John Doe'
                }
            },
            'charge_data': {
                'reference': f'test_complete_flow_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'test_complete_flow': True
                }
            }
        }
        
        result = general_flow.complete_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Complete payment flow successful')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Complete payment flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_card_payment_flow(self, general_flow, amount):
        """Test complete card payment flow"""
        self.stdout.write('\n=== Testing Complete Card Payment Flow ===')
        
        payment_data = {
            'customer_data': {
                'email': f'card_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'Card',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000001'
                }
            },
            'payment_method_data': {
                'type': 'card',
                'card': {
                    'card_number': '4084084084084081',  # Valid test card
                    'cvv': '123',
                    'expiry_month': '12',
                    'expiry_year': '30',
                    'cardholder_name': 'Card User'
                }
            },
            'charge_data': {
                'reference': f'card_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'payment_type': 'card',
                    'test_card_payment': True
                }
            }
        }
        
        result = general_flow.complete_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Card payment flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Card payment flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_mobile_money_flow(self, general_flow, amount):
        """Test complete mobile money payment flow"""
        self.stdout.write('\n=== Testing Complete Mobile Money Payment Flow ===')
        
        payment_data = {
            'customer_data': {
                'email': f'mobile_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'Mobile',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000002'
                }
            },
            'payment_method_data': {
                'type': 'mobile_money',
                'mobile_money': {
                    'country_code': '256',
                    'network': 'MTN',
                    'phone_number': '700000002'
                }
            },
            'charge_data': {
                'reference': f'mobile_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'payment_type': 'mobile_money',
                    'test_mobile_payment': True
                }
            }
        }
        
        result = general_flow.complete_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Mobile money payment flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Mobile money payment flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_all_steps(self, general_flow, amount):
        """Test all steps of the general flow"""
        self.stdout.write('\n=== Testing All Steps of General Flow ===')
        
        # Step 1: Customer Creation
        customer_result = self._test_customer_creation(general_flow)
        if not customer_result['success']:
            return
        
        # Step 2: Payment Method Creation
        self._test_payment_method_creation(general_flow)
        
        # Step 3: Charge Initiation
        charge_result = self._test_charge_initiation(general_flow, amount)
        if not charge_result['success']:
            return
        
        # Step 4: Charge Authorization (if needed)
        if charge_result.get('next_action'):
            self._test_charge_authorization(general_flow)
        
        # Step 5: Payment Verification
        self._test_payment_verification(general_flow)
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ All steps of general flow tested successfully')
        ) 