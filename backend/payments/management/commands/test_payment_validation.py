from django.core.management.base import BaseCommand
from payments.models import PaymentTransaction, PaymentMethod
from payments.serializers import PaymentTransactionCreateSerializer
from users.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test payment validation for different payment types'

    def handle(self, *args, **options):
        # Get a test user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
        
        # Get payment methods
        card_method = PaymentMethod.objects.filter(payment_type='card').first()
        mobile_method = PaymentMethod.objects.filter(payment_type='mobile_money').first()
        cash_method = PaymentMethod.objects.filter(payment_type='cash').first()
        
        if not all([card_method, mobile_method, cash_method]):
            self.stdout.write(self.style.ERROR('Payment methods not found. Run setup_payment_methods first.'))
            return
        
        self.stdout.write('Testing payment validation...\n')
        
        # Test 1: Valid card payment
        self.stdout.write('1. Testing valid card payment...')
        card_data = {
            'transaction_type': 'order',
            'amount': Decimal('50000'),
            'currency': 'UGX',
            'payment_method': card_method.id,
            'redirect_url': 'https://example.com/redirect',
            'callback_url': 'https://example.com/callback',
            'description': 'Test card payment'
        }
        
        try:
            serializer = PaymentTransactionCreateSerializer(data=card_data, context={'request': type('MockRequest', (), {'user': user})()})
            if serializer.is_valid():
                transaction = serializer.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Card payment created: {transaction.transaction_id}'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Card payment validation failed: {serializer.errors}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Card payment error: {str(e)}'))
        
        # Test 2: Valid mobile money payment
        self.stdout.write('\n2. Testing valid mobile money payment...')
        mobile_data = {
            'transaction_type': 'order',
            'amount': Decimal('25000'),
            'currency': 'UGX',
            'payment_method': mobile_method.id,
            'redirect_url': 'https://example.com/redirect',
            'description': 'Test mobile money payment'
        }
        
        try:
            serializer = PaymentTransactionCreateSerializer(data=mobile_data, context={'request': type('MockRequest', (), {'user': user})()})
            if serializer.is_valid():
                transaction = serializer.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Mobile money payment created: {transaction.transaction_id}'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Mobile money payment validation failed: {serializer.errors}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Mobile money payment error: {str(e)}'))
        
        # Test 3: Valid cash payment
        self.stdout.write('\n3. Testing valid cash payment...')
        cash_data = {
            'transaction_type': 'order',
            'amount': Decimal('10000'),
            'currency': 'UGX',
            'payment_method': cash_method.id,
            'description': 'Test cash payment'
        }
        
        try:
            serializer = PaymentTransactionCreateSerializer(data=cash_data, context={'request': type('MockRequest', (), {'user': user})()})
            if serializer.is_valid():
                transaction = serializer.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Cash payment created: {transaction.transaction_id}'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Cash payment validation failed: {serializer.errors}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Cash payment error: {str(e)}'))
        
        # Test 4: Invalid card payment (missing redirect_url)
        self.stdout.write('\n4. Testing invalid card payment (missing redirect_url)...')
        invalid_card_data = {
            'transaction_type': 'order',
            'amount': Decimal('50000'),
            'currency': 'UGX',
            'payment_method': card_method.id,
            'callback_url': 'https://example.com/callback',
            'description': 'Test invalid card payment'
        }
        
        try:
            serializer = PaymentTransactionCreateSerializer(data=invalid_card_data, context={'request': type('MockRequest', (), {'user': user})()})
            if serializer.is_valid():
                self.stdout.write(self.style.ERROR('✗ Invalid card payment should have failed validation'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Invalid card payment correctly rejected: {serializer.errors}'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✓ Invalid card payment correctly rejected: {str(e)}'))
        
        # Test 5: Invalid amount (below minimum)
        self.stdout.write('\n5. Testing invalid amount (below minimum)...')
        low_amount_data = {
            'transaction_type': 'order',
            'amount': Decimal('500'),  # Below minimum of 1000
            'currency': 'UGX',
            'payment_method': card_method.id,
            'redirect_url': 'https://example.com/redirect',
            'callback_url': 'https://example.com/callback',
            'description': 'Test low amount payment'
        }
        
        try:
            serializer = PaymentTransactionCreateSerializer(data=low_amount_data, context={'request': type('MockRequest', (), {'user': user})()})
            if serializer.is_valid():
                self.stdout.write(self.style.ERROR('✗ Low amount payment should have failed validation'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Low amount payment correctly rejected: {serializer.errors}'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✓ Low amount payment correctly rejected: {str(e)}'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Payment validation testing completed!') 