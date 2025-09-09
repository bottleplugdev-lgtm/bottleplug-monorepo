from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
import logging

from orders.models import Invoice
from payments.models import PaymentTransaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check for overdue invoices and update their status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('Starting overdue invoice check...')
        )
        
        # Get current date
        current_date = timezone.now()
        
        # Find invoices that are not paid and have due dates in the past
        overdue_candidates = Invoice.objects.filter(
            status__in=['draft', 'sent'],  # Only check non-paid statuses (excludes paid, overdue, cancelled, etc.)
            due_date__lt=current_date,     # Due date is in the past
        ).select_related('order')
        
        self.stdout.write(f"Found {overdue_candidates.count()} invoices with due dates in the past")
        
        updated_count = 0
        skipped_count = 0
        
        for invoice in overdue_candidates:
            try:
                # Check if the attached order is fully paid
                order = invoice.order
                if not order:
                    if verbose:
                        self.stdout.write(
                            f"⚠️  Invoice {invoice.invoice_number}: No order attached, skipping"
                        )
                    skipped_count += 1
                    continue
                
                # Calculate total paid for this order
                total_paid = PaymentTransaction.objects.filter(
                    order=order,
                    status='successful'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                # Check if order is fully paid
                order_total = order.total_amount
                is_fully_paid = total_paid >= order_total
                
                if verbose:
                    self.stdout.write(
                        f"Invoice {invoice.invoice_number}: "
                        f"Order total: ${order_total}, "
                        f"Total paid: ${total_paid}, "
                        f"Fully paid: {is_fully_paid}"
                    )
                
                # Only mark as overdue if the order is NOT fully paid
                if not is_fully_paid:
                    if not dry_run:
                        invoice.status = 'overdue'
                        invoice.save(update_fields=['status'])
                        logger.info(
                            f"Invoice {invoice.invoice_number} marked as overdue. "
                            f"Order {order.order_number} not fully paid "
                            f"(${total_paid}/{order_total})"
                        )
                    
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Invoice {invoice.invoice_number} marked as overdue "
                            f"(Order {order.order_number}: ${total_paid}/${order_total})"
                        )
                    )
                else:
                    if verbose:
                        self.stdout.write(
                            f"⏭️  Invoice {invoice.invoice_number}: Order fully paid, skipping"
                        )
                    skipped_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Error processing invoice {invoice.invoice_number}: {str(e)}"
                    )
                )
                logger.error(f"Error processing invoice {invoice.invoice_number}: {str(e)}")
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write("OVERDUE INVOICE CHECK SUMMARY")
        self.stdout.write("="*50)
        self.stdout.write(f"Total invoices checked: {overdue_candidates.count()}")
        self.stdout.write(f"Invoices marked as overdue: {updated_count}")
        self.stdout.write(f"Invoices skipped: {skipped_count}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN - No changes were made to the database")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ Overdue invoice check completed successfully")
            ) 