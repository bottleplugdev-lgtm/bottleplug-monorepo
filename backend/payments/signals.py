from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PaymentTransaction
from .services import update_invoice_status_on_order_payment, create_receipt_for_successful_payment
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentTransaction)
def handle_payment_transaction_update(sender, instance, created, **kwargs):
    """
    Signal handler to update invoice status and create payment receipts when payment transactions are created or updated.
    This ensures that when an order is fully paid, all related invoices are marked as paid,
    the order status is updated from 'pending' to 'confirmed', and a payment receipt is created (not an order delivery receipt).
    """
    try:
        # Check if this is a successful payment transaction
        if instance.status in ['successful', 'paid', 'done']:
            logger.info(f"Payment transaction {instance.transaction_id} marked as successful. Processing updates...")
            
            # Create payment receipt for successful payment (decoupled from order delivery receipts)
            receipt_result = create_receipt_for_successful_payment(instance)
            
            if receipt_result['success']:
                if receipt_result.get('receipt_created', False):
                    logger.info(f"✓ {receipt_result['message']}")
                else:
                    logger.debug(f"Receipt creation: {receipt_result['message']}")
            else:
                logger.error(f"✗ Receipt creation failed: {receipt_result.get('error', 'Unknown error')}")
        
        # Only process invoice and order status updates for order payments
        if (instance.transaction_type == 'order' and 
            instance.order and 
            instance.status in ['successful', 'paid']):
            
            logger.info(f"Payment transaction {instance.transaction_id} updated for order {instance.order.id}. Checking invoice and order status...")
            
            # Call the service to update invoice status and order status
            result = update_invoice_status_on_order_payment(instance.order.id)
            
            if result['success']:
                invoices_updated = result.get('invoices_updated', 0)
                order_status_updated = result.get('order_status_updated', False)
                
                if invoices_updated > 0:
                    logger.info(f"Successfully updated {invoices_updated} invoice(s) to paid status for order {instance.order.id}")
                
                if order_status_updated:
                    logger.info(f"Successfully updated order {instance.order.id} status from 'pending' to 'confirmed'")
                
                if invoices_updated == 0 and not order_status_updated:
                    logger.debug(f"No updates needed for order {instance.order.id}. Total paid: {result['total_paid']}, Order total: {result['order_total']}")
            else:
                logger.error(f"Failed to update invoice/order status for order {instance.order.id}: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        logger.error(f"Error in payment transaction signal handler: {str(e)}")
        # Don't raise the exception to avoid breaking the payment transaction save 