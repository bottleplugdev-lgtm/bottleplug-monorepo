from django.core.management.base import BaseCommand
from payments.models import PaymentMethod


class Command(BaseCommand):
    help = 'Set up default payment methods for Uganda'

    def handle(self, *args, **options):
        self.stdout.write('Setting up Uganda payment methods...')
        
        # Default payment methods for Uganda
        payment_methods = [
            {
                'name': 'Credit/Debit Card',
                'payment_type': 'card',
                'flutterwave_code': 'card',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': 100,
                'max_amount': 7000000,
                'processing_fee': 0.0,
                'fixed_fee': 0.0,
                'is_active': True
            },
            {
                'name': 'Mobile Money',
                'payment_type': 'mobile_money',
                'flutterwave_code': 'mobile_money',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': 100,
                'max_amount': 7000000,
                'processing_fee': 0.0,
                'fixed_fee': 0.0,
                'is_active': True
            },
            {
                'name': 'M-Pesa',
                'payment_type': 'mpesa',
                'flutterwave_code': 'mpesa',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': 100,
                'max_amount': 7000000,
                'processing_fee': 0.0,
                'fixed_fee': 0.0,
                'is_active': True
            },
            {
                'name': 'Bank Transfer',
                'payment_type': 'bank',
                'flutterwave_code': 'bank transfer',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': 1000,
                'max_amount': 3000000,
                'processing_fee': 0.0,
                'fixed_fee': 0.0,
                'is_active': True
            },
            {
                'name': 'Cash Payment',
                'payment_type': 'cash',
                'flutterwave_code': 'cash',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': 0,
                'max_amount': None,  # Unlimited
                'processing_fee': 0.0,
                'fixed_fee': 0.0,
                'is_active': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for method_data in payment_methods:
            payment_method, created = PaymentMethod.objects.get_or_create(
                flutterwave_code=method_data['flutterwave_code'],
                country_code=method_data['country_code'],
                defaults=method_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created: {payment_method.name}')
            else:
                # Update existing method
                for key, value in method_data.items():
                    setattr(payment_method, key, value)
                payment_method.save()
                updated_count += 1
                self.stdout.write(f'Updated: {payment_method.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up {created_count} new and updated {updated_count} payment methods for Uganda'
            )
        ) 