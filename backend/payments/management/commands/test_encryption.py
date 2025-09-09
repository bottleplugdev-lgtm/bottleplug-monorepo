from django.core.management.base import BaseCommand
from payments.encryption import FlutterwaveEncryptor, CardDataValidator
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave encryption functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-encryption',
            action='store_true',
            help='Test encryption functionality',
        )
        parser.add_argument(
            '--test-validation',
            action='store_true',
            help='Test card data validation',
        )
        parser.add_argument(
            '--test-card',
            action='store_true',
            help='Test complete card encryption flow',
        )

    def handle(self, *args, **options):
        test_encryption = options['test_encryption']
        test_validation = options['test_validation']
        test_card = options['test_card']
        
        self.stdout.write('Testing Flutterwave Encryption Functionality')
        
        # Initialize encryptor
        encryptor = FlutterwaveEncryptor()
        
        # Check encryption status
        status = encryptor.get_encryption_status()
        self.stdout.write(f'\nEncryption Status:')
        self.stdout.write(f'  Configured: {status["configured"]}')
        self.stdout.write(f'  Key Length: {status["key_length"]}')
        self.stdout.write(f'  Key Preview: {status["key_preview"]}')
        
        if not status['configured']:
            self.stdout.write(
                self.style.WARNING('⚠️ Encryption key not configured. Some tests will be skipped.')
            )
        
        # Test encryption functionality
        if test_encryption:
            self._test_encryption(encryptor)
        
        # Test validation functionality
        if test_validation:
            self._test_validation()
        
        # Test complete card flow
        if test_card:
            self._test_card_encryption(encryptor)
        
        # If no specific test requested, run all tests
        if not any([test_encryption, test_validation, test_card]):
            self._test_encryption(encryptor)
            self._test_validation()
            self._test_card_encryption(encryptor)
    
    def _test_encryption(self, encryptor):
        """Test basic encryption functionality"""
        self.stdout.write('\n=== Testing Encryption Functionality ===')
        
        try:
            # Test nonce generation
            nonce1 = encryptor.generate_nonce()
            nonce2 = encryptor.generate_nonce()
            self.stdout.write(f'Nonce 1: {nonce1}')
            self.stdout.write(f'Nonce 2: {nonce2}')
            self.stdout.write(f'Nonces different: {nonce1 != nonce2}')
            
            if encryptor.is_configured():
                # Test basic encryption
                test_text = "Hello, Flutterwave!"
                encrypted = encryptor.encrypt(test_text, nonce1)
                self.stdout.write(f'Original: {test_text}')
                self.stdout.write(f'Encrypted: {encrypted}')
                self.stdout.write(
                    self.style.SUCCESS('✅ Basic encryption working')
                )
                
                # Test dictionary encryption
                test_dict = {
                    'key1': 'value1',
                    'key2': 'value2',
                    'number': '12345'
                }
                encrypted_dict = encryptor.encrypt_dict(test_dict)
                self.stdout.write(f'Original Dict: {test_dict}')
                self.stdout.write(f'Encrypted Dict: {encrypted_dict}')
                self.stdout.write(
                    self.style.SUCCESS('✅ Dictionary encryption working')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Skipping encryption tests - key not configured')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Encryption test failed: {e}')
            )
    
    def _test_validation(self):
        """Test card data validation"""
        self.stdout.write('\n=== Testing Card Data Validation ===')
        
        # Test valid card data
        valid_card = {
            'card_number': '4111111111111111',  # Valid Visa
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cardholder_name': 'John Doe'
        }
        
        is_valid, errors = CardDataValidator.validate_card_data(valid_card)
        self.stdout.write(f'Valid Card Test:')
        self.stdout.write(f'  Valid: {is_valid}')
        self.stdout.write(f'  Errors: {errors}')
        
        if is_valid:
            self.stdout.write(
                self.style.SUCCESS('✅ Valid card data validation working')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Valid card data validation failed')
            )
        
        # Test invalid card data
        invalid_cards = [
            {
                'card_number': '1234567890123456',  # Invalid
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2025',
                'cardholder_name': 'John Doe',
                'description': 'Invalid card number'
            },
            {
                'card_number': '4111111111111111',
                'cvv': '12',  # Too short
                'expiry_month': '12',
                'expiry_year': '2025',
                'cardholder_name': 'John Doe',
                'description': 'Invalid CVV'
            },
            {
                'card_number': '4111111111111111',
                'cvv': '123',
                'expiry_month': '13',  # Invalid month
                'expiry_year': '2025',
                'cardholder_name': 'John Doe',
                'description': 'Invalid expiry month'
            },
            {
                'card_number': '4111111111111111',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2020',  # Expired
                'cardholder_name': 'John Doe',
                'description': 'Expired card'
            },
            {
                'card_number': '4111111111111111',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2025',
                'cardholder_name': '',  # Empty name
                'description': 'Empty cardholder name'
            }
        ]
        
        for invalid_card in invalid_cards:
            description = invalid_card.pop('description')
            is_valid, errors = CardDataValidator.validate_card_data(invalid_card)
            self.stdout.write(f'\n{description}:')
            self.stdout.write(f'  Valid: {is_valid}')
            self.stdout.write(f'  Errors: {errors}')
            
            if not is_valid:
                self.stdout.write(
                    self.style.SUCCESS('✅ Invalid card data correctly rejected')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Invalid card data incorrectly accepted')
                )
    
    def _test_card_encryption(self, encryptor):
        """Test complete card encryption flow"""
        self.stdout.write('\n=== Testing Card Encryption Flow ===')
        
        # Test card data
        card_data = {
            'card_number': '4111111111111111',
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cardholder_name': 'John Doe'
        }
        
        try:
            # Validate card data
            is_valid, errors = CardDataValidator.validate_card_data(card_data)
            if not is_valid:
                self.stdout.write(
                    self.style.ERROR(f'❌ Card validation failed: {errors}')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS('✅ Card validation passed')
            )
            
            # Encrypt card data
            if encryptor.is_configured():
                encrypted_card = encryptor.encrypt_card_data(card_data)
                self.stdout.write(f'Original Card Data: {card_data}')
                self.stdout.write(f'Encrypted Card Data: {encrypted_card}')
                
                # Check encrypted structure
                required_fields = ['nonce', 'encrypted_card_number', 'encrypted_cvv', 
                                'encrypted_expiry_month', 'encrypted_expiry_year']
                missing_fields = [field for field in required_fields if field not in encrypted_card]
                
                if not missing_fields:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Card encryption structure correct')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Missing encrypted fields: {missing_fields}')
                    )
                
                # Check that cardholder name is not encrypted
                if 'cardholder_name' in encrypted_card:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Cardholder name preserved (not encrypted)')
                    )
                
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Skipping card encryption - key not configured')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Card encryption test failed: {e}')
            )
        
        self.stdout.write('\nEncryption testing completed') 