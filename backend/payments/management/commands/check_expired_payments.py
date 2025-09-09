from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import PaymentTransaction
from payments.services import FlutterwaveService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check for expired payments and update their status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force check all pending payments regardless of expiration time',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']
        
        self.stdout.write('Checking for expired payments...')
        
        # Get pending transactions that have expired
        now = timezone.now()
        expired_transactions = PaymentTransaction.objects.filter(
            status='pending',
            expired_at__lt=now
        )
        
        if force:
            # If force is used, check all pending transactions
            expired_transactions = PaymentTransaction.objects.filter(status='pending')
            self.stdout.write(f'Force checking all {expired_transactions.count()} pending transactions...')
        else:
            self.stdout.write(f'Found {expired_transactions.count()} expired transactions...')
        
        if not expired_transactions.exists():
            self.stdout.write(self.style.SUCCESS('No expired transactions found.'))
            return
        
        # Initialize Flutterwave service
        flutterwave_service = FlutterwaveService()
        
        processed_count = 0
        expired_count = 0
        error_count = 0
        
        for transaction in expired_transactions:
            try:
                self.stdout.write(f'Processing transaction: {transaction.transaction_id}')
                
                if dry_run:
                    self.stdout.write(f'[DRY RUN] Would check transaction: {transaction.transaction_id}')
                    continue
                
                # Check if payment was actually completed via Flutterwave
                if transaction.flutterwave_reference:
                    # Verify payment status with Flutterwave
                    verification_result = flutterwave_service.verify_payment(transaction.flutterwave_reference)
                    
                    if verification_result['success'] and verification_result.get('verified'):
                        # Payment was successful, update status
                        transaction.mark_as_paid()
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Transaction {transaction.transaction_id} marked as successful')
                        )
                        processed_count += 1
                    else:
                        # Payment failed or not completed, mark as expired
                        transaction.mark_as_expired()
                        self.stdout.write(
                            self.style.WARNING(f'✗ Transaction {transaction.transaction_id} marked as expired')
                        )
                        expired_count += 1
                else:
                    # No Flutterwave reference, mark as expired
                    transaction.mark_as_expired()
                    self.stdout.write(
                        self.style.WARNING(f'✗ Transaction {transaction.transaction_id} marked as expired (no Flutterwave reference)')
                    )
                    expired_count += 1
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing transaction {transaction.transaction_id}: {str(e)}')
                )
                logger.error(f'Error processing expired transaction {transaction.transaction_id}: {e}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY:')
        self.stdout.write(f'Processed: {processed_count}')
        self.stdout.write(f'Expired: {expired_count}')
        self.stdout.write(f'Errors: {error_count}')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS('Payment status check completed successfully')) 