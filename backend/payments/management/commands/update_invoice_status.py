from django.core.management.base import BaseCommand
from django.db.models import Sum
from orders.models import Order, Invoice
from payments.models import PaymentTransaction
from payments.services import update_invoice_status_on_order_payment, create_receipt_for_successful_payment
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update invoice status to paid for orders that are fully paid and create receipts for successful payments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order-id',
            type=int,
            help='Update invoices for a specific order ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all orders regardless of current status',
        )
        parser.add_argument(
            '--create-receipts',
            action='store_true',
            help='Create receipts for successful payments',
        )

    def handle(self, *args, **options):
        order_id = options['order_id']
        dry_run = options['dry_run']
        force = options['force']
        create_receipts = options['create_receipts']
        
        self.stdout.write('Checking for orders with unpaid invoices...')
        
        if create_receipts:
            self.stdout.write('Creating receipts for successful payments...')
            self._create_receipts_for_successful_payments(dry_run)
        
        if order_id:
            # Process specific order
            try:
                order = Order.objects.get(id=order_id)
                self._process_order(order, dry_run)
            except Order.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Order with ID {order_id} does not exist')
                )
                return
        else:
            # Process all orders
            orders = Order.objects.all()
            
            if not force:
                # Only process orders that have invoices
                orders = orders.filter(invoices__isnull=False).distinct()
            
            self.stdout.write(f'Found {orders.count()} orders to check...')
            
            processed_count = 0
            updated_count = 0
            
            for order in orders:
                result = self._process_order(order, dry_run)
                processed_count += 1
                if result:
                    updated_count += result
            
            self.stdout.write('\n' + '='*50)
            self.stdout.write('SUMMARY:')
            self.stdout.write(f'Orders processed: {processed_count}')
            self.stdout.write(f'Invoices updated: {updated_count}')
            self.stdout.write('='*50)
            
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
            else:
                self.stdout.write(self.style.SUCCESS('Invoice status update completed successfully'))
    
    def _create_receipts_for_successful_payments(self, dry_run):
        """Create receipts for successful payment transactions"""
        successful_payments = PaymentTransaction.objects.filter(
            status__in=['successful', 'paid', 'done']
        )
        
        self.stdout.write(f'Found {successful_payments.count()} successful payment transactions')
        
        receipts_created = 0
        receipts_skipped = 0
        
        for payment in successful_payments:
            if dry_run:
                self.stdout.write(f'[DRY RUN] Would create receipt for payment {payment.transaction_id}')
                receipts_created += 1
            else:
                result = create_receipt_for_successful_payment(payment)
                if result['success']:
                    if result.get('receipt_created', False):
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created receipt {result["receipt_number"]} for payment {payment.transaction_id}')
                        )
                        receipts_created += 1
                    else:
                        self.stdout.write(f'Receipt already exists for payment {payment.transaction_id}')
                        receipts_skipped += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to create receipt for payment {payment.transaction_id}: {result.get("error", "Unknown error")}')
                    )
        
        self.stdout.write(f'\nReceipt creation summary:')
        self.stdout.write(f'Receipts created: {receipts_created}')
        self.stdout.write(f'Receipts skipped (already exist): {receipts_skipped}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No receipts were actually created'))
        else:
            self.stdout.write(self.style.SUCCESS('Receipt creation completed'))
    
    def _process_order(self, order, dry_run):
        """Process a single order and update its invoices if needed"""
        try:
            # Get all successful payment transactions for this order
            successful_payments = PaymentTransaction.objects.filter(
                order=order,
                status__in=['successful', 'paid']
            )
            
            # Calculate total amount paid from payment transactions
            total_paid = successful_payments.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Use the order's total_amount (which is calculated as subtotal + tax + delivery_fee - discount)
            total_order_amount = order.total_amount
            
            # Get all invoices for this order
            invoices = Invoice.objects.filter(order=order)
            
            if not invoices.exists():
                self.stdout.write(f'Order {order.order_number}: No invoices found')
                return 0
            
            unpaid_invoices = invoices.filter(status__in=['draft', 'sent', 'overdue'])
            
            if not unpaid_invoices.exists():
                self.stdout.write(f'Order {order.order_number}: All invoices already paid')
                return 0
            
            # Check if order is fully paid
            if total_paid >= total_order_amount:
                self.stdout.write(
                    f'Order {order.order_number}: Fully paid (${total_paid}/${order.total_amount}). '
                    f'Found {unpaid_invoices.count()} unpaid invoice(s)'
                )
                
                if dry_run:
                    self.stdout.write(f'[DRY RUN] Would mark {unpaid_invoices.count()} invoice(s) as paid')
                    # Check if order status would be updated
                    if order.status == 'pending':
                        self.stdout.write(f'[DRY RUN] Would update order status from "pending" to "confirmed"')
                    return unpaid_invoices.count()
                else:
                    # Call the service to update invoice status and order status
                    result = update_invoice_status_on_order_payment(order.id)
                    
                    if result['success']:
                        updated_invoices = result.get('invoices_updated', 0)
                        order_status_updated = result.get('order_status_updated', False)
                        
                        if updated_invoices > 0:
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Updated {updated_invoices} invoice(s) to paid status')
                            )
                        
                        if order_status_updated:
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Updated order status from "pending" to "confirmed"')
                            )
                        
                        return updated_invoices
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'✗ Failed to update invoices: {result.get("error", "Unknown error")}')
                        )
                        return 0
            else:
                self.stdout.write(
                    f'Order {order.order_number}: Not fully paid (${total_paid}/${order.total_amount}). '
                    f'Skipping invoice updates'
                )
                return 0
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing order {order.order_number}: {str(e)}')
            )
            logger.error(f'Error processing order {order.order_number}: {e}')
            return 0 