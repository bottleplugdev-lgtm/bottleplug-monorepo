from django.core.management.base import BaseCommand
from payments.general_flow import FlutterwaveGeneralFlow
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test different authorization types in Flutterwave General Flow'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-otp',
            action='store_true',
            help='Test OTP authorization flow',
        )
        parser.add_argument(
            '--test-avs',
            action='store_true',
            help='Test AVS (Address Verification) authorization flow',
        )
        parser.add_argument(
            '--test-pin',
            action='store_true',
            help='Test PIN authorization flow',
        )
        parser.add_argument(
            '--test-payment-instructions',
            action='store_true',
            help='Test payment instructions flow',
        )
        parser.add_argument(
            '--test-all',
            action='store_true',
            help='Test all authorization types',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=1000.0,
            help='Payment amount (default: 1000.0)',
        )

    def handle(self, *args, **options):
        test_otp = options['test_otp']
        test_avs = options['test_avs']
        test_pin = options['test_pin']
        test_payment_instructions = options['test_payment_instructions']
        test_all = options['test_all']
        amount = options['amount']
        
        self.stdout.write('Testing Flutterwave Authorization Types')
        
        # Initialize general flow
        general_flow = FlutterwaveGeneralFlow()
        
        if test_otp:
            self._test_otp_authorization(general_flow, amount)
        elif test_avs:
            self._test_avs_authorization(general_flow, amount)
        elif test_pin:
            self._test_pin_authorization(general_flow, amount)
        elif test_payment_instructions:
            self._test_payment_instructions(general_flow, amount)
        elif test_all:
            self._test_all_authorization_types(general_flow, amount)
        else:
            # Test all by default
            self._test_all_authorization_types(general_flow, amount)
    
    def _test_otp_authorization(self, general_flow, amount):
        """Test OTP authorization flow"""
        self.stdout.write('\n=== Testing OTP Authorization Flow ===')
        
        payment_data = {
            'customer_data': {
                'email': f'otp_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'OTP',
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
                    'card_number': '4084084084084081',
                    'cvv': '123',
                    'expiry_month': '12',
                    'expiry_year': '30',
                    'cardholder_name': 'OTP User'
                }
            },
            'charge_data': {
                'reference': f'otp_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'payment_type': 'card',
                    'authorization_type': 'otp',
                    'test_otp_flow': True
                }
            },
            'authorization_data': {
                'type': 'otp',
                'otp': {
                    'code': '123456'
                }
            }
        }
        
        result = general_flow.complete_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ OTP authorization flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ OTP authorization flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_avs_authorization(self, general_flow, amount):
        """Test AVS (Address Verification) authorization flow"""
        self.stdout.write('\n=== Testing AVS Authorization Flow ===')
        
        payment_data = {
            'customer_data': {
                'email': f'avs_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'AVS',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000002'
                }
            },
            'payment_method_data': {
                'type': 'card',
                'card': {
                    'card_number': '4084084084084081',
                    'cvv': '123',
                    'expiry_month': '12',
                    'expiry_year': '30',
                    'cardholder_name': 'AVS User'
                }
            },
            'charge_data': {
                'reference': f'avs_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'payment_type': 'card',
                    'authorization_type': 'avs',
                    'test_avs_flow': True
                }
            },
            'authorization_data': {
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
        }
        
        result = general_flow.complete_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ AVS authorization flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ AVS authorization flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_pin_authorization(self, general_flow, amount):
        """Test PIN authorization flow"""
        self.stdout.write('\n=== Testing PIN Authorization Flow ===')
        
        payment_data = {
            'customer_data': {
                'email': f'pin_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'PIN',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000003'
                }
            },
            'payment_method_data': {
                'type': 'card',
                'card': {
                    'card_number': '4084084084084081',
                    'cvv': '123',
                    'expiry_month': '12',
                    'expiry_year': '30',
                    'cardholder_name': 'PIN User'
                }
            },
            'charge_data': {
                'reference': f'pin_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'payment_type': 'card',
                    'authorization_type': 'pin',
                    'test_pin_flow': True
                }
            },
            'authorization_data': {
                'type': 'pin',
                'pin': {
                    'nonce': 'test_nonce_123',
                    'encrypted_pin': 'test_encrypted_pin_456'
                }
            }
        }
        
        result = general_flow.complete_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ PIN authorization flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ PIN authorization flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_payment_instructions(self, general_flow, amount):
        """Test payment instructions flow"""
        self.stdout.write('\n=== Testing Payment Instructions Flow ===')
        
        payment_data = {
            'customer_data': {
                'email': f'instructions_test_{int(time.time())}@example.com',
                'name': {
                    'first': 'Instructions',
                    'last': 'User'
                },
                'phone': {
                    'country_code': '256',
                    'number': '700000004'
                }
            },
            'payment_method_data': {
                'type': 'mobile_money',
                'mobile_money': {
                    'country_code': '256',
                    'network': 'MTN',
                    'phone_number': '700000004'
                }
            },
            'charge_data': {
                'reference': f'instructions_payment_{int(time.time())}',
                'currency': 'USD',
                'amount': amount,
                'redirect_url': 'https://example.com/return',
                'meta': {
                    'payment_type': 'mobile_money',
                    'authorization_type': 'payment_instructions',
                    'test_instructions_flow': True
                }
            }
        }
        
        result = general_flow.complete_payment_flow(payment_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Payment instructions flow completed successfully')
            )
            self.stdout.write(f'Customer ID: {result["customer_id"]}')
            self.stdout.write(f'Payment Method ID: {result["payment_method_id"]}')
            self.stdout.write(f'Charge ID: {result["charge_id"]}')
            self.stdout.write(f'Status: {result["status"]}')
            
            if 'note' in result:
                self.stdout.write(f'Instructions: {result["note"]}')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Payment instructions flow failed: {result["error"]}')
            )
        
        return result
    
    def _test_all_authorization_types(self, general_flow, amount):
        """Test all authorization types"""
        self.stdout.write('\n=== Testing All Authorization Types ===')
        
        authorization_tests = [
            ('OTP', self._test_otp_authorization),
            ('AVS', self._test_avs_authorization),
            ('PIN', self._test_pin_authorization),
            ('Payment Instructions', self._test_payment_instructions)
        ]
        
        results = {}
        
        for auth_type, test_function in authorization_tests:
            self.stdout.write(f'\n--- Testing {auth_type} Authorization ---')
            try:
                result = test_function(general_flow, amount)
                results[auth_type] = result['success']
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {auth_type} authorization test passed')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ {auth_type} authorization test failed')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ {auth_type} authorization test error: {e}')
                )
                results[auth_type] = False
        
        # Summary
        self.stdout.write('\n=== Authorization Tests Summary ===')
        passed = sum(1 for success in results.values() if success)
        total = len(results)
        
        for auth_type, success in results.items():
            status = '✅ PASS' if success else '❌ FAIL'
            self.stdout.write(f'{auth_type}: {status}')
        
        self.stdout.write(f'\nOverall: {passed}/{total} authorization types passed')
        
        if passed == total:
            self.stdout.write(
                self.style.SUCCESS('🎉 All authorization types working correctly!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Some authorization types need attention')
            )
    
    def _test_authorization_handling(self, general_flow):
        """Test authorization handling logic"""
        self.stdout.write('\n=== Testing Authorization Handling Logic ===')
        
        # Test different next_action types
        test_cases = [
            {
                'type': 'requires_otp',
                'name': 'OTP Authorization',
                'expected': 'otp_required'
            },
            {
                'type': 'requires_additional_fields',
                'name': 'AVS Authorization',
                'expected': 'additional_fields_required'
            },
            {
                'type': 'requires_pin',
                'name': 'PIN Authorization',
                'expected': 'pin_required'
            },
            {
                'type': 'redirect_url',
                'name': 'Redirect Authorization',
                'expected': 'redirect_required'
            },
            {
                'type': 'payment_instruction',
                'name': 'Payment Instructions',
                'expected': 'instructions_provided'
            }
        ]
        
        for test_case in test_cases:
            next_action = {'type': test_case['type']}
            result = general_flow.handle_next_action('test_charge_id', next_action)
            
            if result['type'] == test_case['expected']:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {test_case["name"]} handled correctly')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {test_case["name"]} handling failed')
                )
                self.stdout.write(f'Expected: {test_case["expected"]}, Got: {result["type"]}') 