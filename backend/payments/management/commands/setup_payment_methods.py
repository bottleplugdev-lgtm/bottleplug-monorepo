from django.core.management.base import BaseCommand
from payments.models import PaymentMethod
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up default payment methods for card, mobile money, and cash'

    def handle(self, *args, **options):
        payment_methods = [
            {
                'name': 'Credit/Debit Card',
                'payment_type': 'card',
                'flutterwave_code': 'card',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': Decimal('1000'),
                'max_amount': Decimal('1000000'),
                'processing_fee': Decimal('2.5'),
                'fixed_fee': Decimal('0'),
                'is_active': True
            },
            {
                'name': 'Mobile Money',
                'payment_type': 'mobile_money',
                'flutterwave_code': 'mobilemoneyuganda',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': Decimal('1000'),
                'max_amount': Decimal('500000'),
                'processing_fee': Decimal('1.0'),
                'fixed_fee': Decimal('0'),
                'is_active': True
            },
            {
                'name': 'Cash Payment',
                'payment_type': 'cash',
                'flutterwave_code': 'cash',
                'country_code': 'UG',
                'currency': 'UGX',
                'min_amount': Decimal('100'),
                'max_amount': None,  # No limit for cash
                'processing_fee': Decimal('0'),
                'fixed_fee': Decimal('0'),
                'is_active': True
            }
        ]

        created_count = 0
        updated_count = 0

        for method_data in payment_methods:
            payment_method, created = PaymentMethod.objects.get_or_create(
                flutterwave_code=method_data['flutterwave_code'],
                defaults=method_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created payment method: {payment_method.name} ({payment_method.payment_type})'
                    )
                )
            else:
                # Update existing payment method
                for key, value in method_data.items():
                    setattr(payment_method, key, value)
                payment_method.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Updated payment method: {payment_method.name} ({payment_method.payment_type})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Payment methods setup completed. Created: {created_count}, Updated: {updated_count}'
            )
        ) 