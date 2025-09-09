from celery import shared_task
from django.utils import timezone
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_expired_payments():
    """
    Celery task to check for expired payments and update their status
    This task runs every 5 minutes to check for expired payments
    """
    try:
        logger.info("Starting automatic payment status check...")
        
        # Call the management command
        call_command('check_expired_payments')
        
        logger.info("Payment status check completed successfully")
        return {
            'success': True,
            'message': 'Payment status check completed'
        }
        
    except Exception as e:
        logger.error(f"Error in payment status check task: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def force_check_all_payments():
    """
    Celery task to force check all pending payments regardless of expiration time
    This can be used for manual intervention or system recovery
    """
    try:
        logger.info("Starting forced payment status check...")
        
        # Call the management command with force flag
        call_command('check_expired_payments', force=True)
        
        logger.info("Forced payment status check completed successfully")
        return {
            'success': True,
            'message': 'Forced payment status check completed'
        }
        
    except Exception as e:
        logger.error(f"Error in forced payment status check task: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_old_payment_webhooks():
    """
    Celery task to cleanup old webhook data
    This task runs daily to remove webhook data older than 30 days
    """
    try:
        from .models import PaymentWebhook
        from datetime import timedelta
        
        # Delete webhooks older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = PaymentWebhook.objects.filter(
            received_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old payment webhooks")
        return {
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} old webhooks'
        }
        
    except Exception as e:
        logger.error(f"Error in webhook cleanup task: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def verify_payment_status(transaction_id):
    """
    Celery task to verify a specific payment status
    This can be called for individual payment verification
    """
    try:
        from .models import PaymentTransaction
        from .services import FlutterwaveService
        
        # Get the transaction
        try:
            transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Transaction {transaction_id} not found")
            return {
                'success': False,
                'error': f'Transaction {transaction_id} not found'
            }
        
        # Skip if already processed
        if transaction.status in ['successful', 'paid', 'failed', 'expired']:
            logger.info(f"Transaction {transaction_id} already processed with status: {transaction.status}")
            return {
                'success': True,
                'message': f'Transaction already processed with status: {transaction.status}'
            }
        
        # Verify with Flutterwave
        flutterwave_service = FlutterwaveService()
        
        if transaction.flutterwave_reference:
            verification_result = flutterwave_service.verify_payment(transaction.flutterwave_reference)
            
            if verification_result['success'] and verification_result.get('verified'):
                transaction.mark_as_paid()
                logger.info(f"Transaction {transaction_id} verified and marked as paid")
                return {
                    'success': True,
                    'message': 'Payment verified and marked as paid'
                }
            else:
                # Check if expired
                if transaction.is_expired:
                    transaction.mark_as_expired()
                    logger.info(f"Transaction {transaction_id} marked as expired")
                    return {
                        'success': True,
                        'message': 'Payment marked as expired'
                    }
                else:
                    logger.info(f"Transaction {transaction_id} still pending")
                    return {
                        'success': True,
                        'message': 'Payment still pending'
                    }
        else:
            # No Flutterwave reference, check if expired
            if transaction.is_expired:
                transaction.mark_as_expired()
                logger.info(f"Transaction {transaction_id} marked as expired (no Flutterwave reference)")
                return {
                    'success': True,
                    'message': 'Payment marked as expired'
                }
            else:
                logger.info(f"Transaction {transaction_id} still pending (no Flutterwave reference)")
                return {
                    'success': True,
                    'message': 'Payment still pending'
                }
                
    except Exception as e:
        logger.error(f"Error verifying payment {transaction_id}: {e}")
        return {
            'success': False,
            'error': str(e)
        } 