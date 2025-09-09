import requests
import json
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class FlutterwaveService:
    """
    Flutterwave payment service integration with OAuth 2.0 authentication
    """
    
    def __init__(self):
        # OAuth 2.0 Authentication Manager
        from .auth_manager import FlutterwaveAuthManager
        self.auth_manager = FlutterwaveAuthManager()
        
        # Environment configuration
        self.environment = getattr(settings, 'FLUTTERWAVE_ENVIRONMENT', 'sandbox')
        
        # Legacy API key settings (fallback)
        self.secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
        self.public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', 'FLWPUBK-097dab2699e3f44fa1fa051376bd63e5-X')
        self.encryption_key = getattr(settings, 'FLUTTERWAVE_ENCRYPTION_KEY', '')
        
        # Initialize encryption
        from .encryption import FlutterwaveEncryptor
        self.encryptor = FlutterwaveEncryptor(self.encryption_key)
        
        # Initialize API versioning
        from .api_versioning import APIVersionManager
        self.version_manager = APIVersionManager()
        
        # Initialize error handling
        from .error_handling import FlutterwaveErrorHandler
        self.error_handler = FlutterwaveErrorHandler()
        
        # Get base URL from version manager
        self.base_url = self.version_manager.get_compatible_url('', self.environment)
        
        # Default settings
        self.default_currency = getattr(settings, 'DEFAULT_PAYMENT_CURRENCY', 'UGX')
        self.default_country = getattr(settings, 'DEFAULT_PAYMENT_COUNTRY', 'UG')
        self.default_payment_options = getattr(settings, 'DEFAULT_PAYMENT_OPTIONS', 'card,mobile_money,mpesa,bank transfer,cash')
        self.default_redirect_url = getattr(settings, 'DEFAULT_REDIRECT_URL', 'boozenation://return')
        
        # Log environment and authentication method being used
        logger.info(f"Flutterwave API Environment: {self.environment.upper()}")
        logger.info(f"Flutterwave API Base URL: {self.base_url}")
        
        if self.auth_manager.is_oauth_configured():
            logger.info("Using OAuth 2.0 authentication for Flutterwave API")
        else:
            logger.warning("OAuth 2.0 not configured, using fallback API key authentication")
            if not self.secret_key:
                logger.warning("Flutterwave secret key not configured - some features may be limited")
        if not self.public_key:
            logger.warning("Flutterwave public key not configured")
    
    def _get_headers(self, include_idempotency=True, include_trace=True, scenario_key=None, custom_idempotency_key=None):
        """
        Get request headers with OAuth 2.0 Bearer token and v4 API headers
        
        Args:
            include_idempotency (bool): Include X-Idempotency-Key header
            include_trace (bool): Include X-Trace-Id header  
            scenario_key (str): Optional scenario key for testing
            custom_idempotency_key (str): Custom idempotency key (if None, auto-generated)
        """
        # Get base headers from auth manager
        base_headers = self.auth_manager.get_v4_headers(
            include_idempotency=include_idempotency,
            include_trace=include_trace,
            scenario_key=scenario_key,
            custom_idempotency_key=custom_idempotency_key
        )
        
        # Make headers compatible with current API version
        return self.version_manager.get_compatible_headers(
            base_headers,
            include_oauth=True,
            include_v4_headers=True,
            include_scenarios=True
        )
    
    def _encrypt_payload(self, payload):
        """Encrypt payload using Flutterwave encryption key"""
        if not self.encryption_key:
            return payload
        
        try:
            import base64
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            
            # Convert payload to JSON string
            json_payload = json.dumps(payload)
            
            # Generate random IV
            import os
            iv = os.urandom(16)
            
            # Create cipher
            cipher = AES.new(self.encryption_key.encode(), AES.MODE_CBC, iv)
            
            # Pad and encrypt
            padded_data = pad(json_payload.encode(), AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Encode to base64
            encrypted_payload = base64.b64encode(encrypted_data).decode()
            iv_b64 = base64.b64encode(iv).decode()
            
            return {
                'client': encrypted_payload,
                'algo': '3DES-24'
            }
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return payload
    
    def create_payment_link(self, transaction):
        """
        Create a payment link for the transaction
        """
        try:
            # Get payment details from metadata if available
            payment_details = {}
            if transaction.metadata and 'payment_details' in transaction.metadata:
                payment_details = transaction.metadata['payment_details']
            
            payload = {
                'tx_ref': transaction.reference,
                'amount': str(transaction.amount),
                'currency': transaction.currency or self.default_currency,
                'redirect_url': transaction.redirect_url or self.default_redirect_url,
                'customer': {
                    'email': transaction.customer_email,
                    'name': transaction.customer_name,
                    'phone_number': transaction.customer_phone or ''
                },
                'customizations': {
                    'title': f'Payment for {transaction.transaction_type}',
                    'description': transaction.description or f'Payment for {transaction.transaction_type}',
                    'logo': getattr(settings, 'SITE_LOGO_URL', '')
                },
                'meta': {
                    'transaction_id': transaction.transaction_id,
                    'transaction_type': transaction.transaction_type,
                    'customer_id': transaction.customer.id
                },
                'payment_options': 'card,mobile_money,mpesa,bank transfer,cash'
            }
            
            # Use v4 API headers with idempotency and trace
            # Use transaction reference as idempotency key for consistency
            idempotency_key = f"payment_{transaction.reference}"
            headers = self._get_headers(
                include_idempotency=True,
                include_trace=True,
                custom_idempotency_key=idempotency_key
            )
            
            # Add payment method specific details
            if transaction.payment_method:
                payload['payment_options'] = transaction.payment_method.flutterwave_code
                
                # Add payment details based on method
                if transaction.payment_method.payment_type == 'card' and payment_details:
                    # Validate card data first
                    from .encryption import CardDataValidator
                    is_valid, errors = CardDataValidator.validate_card_data(payment_details)
                    
                    if not is_valid:
                        logger.error(f"Invalid card data: {errors}")
                        return {
                            'success': False,
                            'error': f"Invalid card data: {', '.join(errors)}"
                        }
                    
                    # Encrypt card data for secure transmission
                    try:
                        encrypted_card = self.encryptor.encrypt_card_data(payment_details)
                        payload['payment_method'] = {
                            'type': 'card',
                            'card': encrypted_card
                        }
                        logger.info("Card data encrypted successfully")
                    except Exception as e:
                        logger.error(f"Card encryption failed: {e}")
                        return {
                            'success': False,
                            'error': f"Card encryption failed: {e}"
                        }
                elif transaction.payment_method.payment_type in ['mobile_money', 'mpesa'] and payment_details:
                    payload['phone_number'] = payment_details.get('phone_number', '')
                    if transaction.payment_method.payment_type == 'mobile_money':
                        payload['network'] = payment_details.get('network', '')
                elif transaction.payment_method.payment_type == 'bank' and payment_details:
                    payload['bank_details'] = {
                        'bank_code': payment_details.get('bank_code', ''),
                        'account_number': payment_details.get('account_number', ''),
                        'account_name': payment_details.get('account_name', '')
                    }
                elif transaction.payment_method.payment_type == 'cash':
                    # For cash payments, we mark it as paid immediately
                    payload['payment_type'] = 'cash'
                    payload['payment_options'] = 'cash'
            
            # Encrypt payload if encryption key is available
            if self.encryption_key:
                payload = self._encrypt_payload(payload)
            
            # For now, we'll create a mock payment URL since we don't have the secret key
            # In production, you would make the actual API call to Flutterwave
            if not self.secret_key:
                # Mock response for development/testing
                mock_payment_url = f"https://checkout.flutterwave.com/v3/hosted/pay/{transaction.reference}"
                transaction.payment_url = mock_payment_url
                transaction.flutterwave_reference = transaction.reference
                transaction.flutterwave_response = {
                    'status': 'success',
                    'message': 'Payment link created (mock)',
                    'data': {
                        'link': mock_payment_url,
                        'reference': transaction.reference,
                        'payment_details': payment_details
                    }
                }
                transaction.save()
                
                return {
                    'success': True,
                    'payment_url': mock_payment_url,
                    'reference': transaction.reference,
                    'data': transaction.flutterwave_response
                }
            
            # Make payload compatible with current API version
            compatible_payload = self.version_manager.get_compatible_payload(
                payload, 
                payment_type=transaction.payment_method.payment_type if transaction.payment_method else None
            )
            
                        # Validate payment data before sending
            is_valid, validation_errors = self.error_handler.validate_payment_data(compatible_payload)
            if not is_valid:
                logger.error(f"Payment validation failed: {validation_errors}")
                return {
                    'success': False,
                    'error': f"Validation failed: {', '.join(validation_errors)}"
                }
            
            # Real API call when secret key is available
            response = requests.post(
                f'{self.base_url}/payments',
                headers=headers,
                json=compatible_payload,
                timeout=30
            )
            
            # Handle response with error handling
            success, result = self.error_handler.handle_response(response, "Payment creation")
            
            if success:
                data = result['data']
                
                # Check for idempotency cache hit
                cache_hit = response.headers.get('X-Idempotency-Cache-Hit', 'false').lower() == 'true'
                if cache_hit:
                    logger.info(f"Idempotency cache hit for payment {transaction.reference}")
                
                if data.get('status') == 'success':
                    payment_data = data.get('data', {})
                    transaction.payment_url = payment_data.get('link')
                    transaction.flutterwave_reference = payment_data.get('reference')
                    transaction.flutterwave_response = data
                    transaction.idempotency_cache_hit = cache_hit
                    transaction.save()
                    
                    return {
                        'success': True,
                        'payment_url': payment_data.get('link'),
                        'reference': payment_data.get('reference'),
                        'data': data,
                        'idempotency_cache_hit': cache_hit
                    }
                else:
                    logger.error(f"Flutterwave payment creation failed: {data}")
                    return {
                        'success': False,
                        'error': data.get('message', 'Payment creation failed'),
                        'idempotency_cache_hit': cache_hit
                    }
            else:
                # Error response handled by error handler
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message'],
                    'retryable': result['retryable']
                }
                
        except Exception as e:
            logger.error(f"Error creating payment link: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, transaction_id):
        """
        Verify payment status with Flutterwave
        """
        try:
            # Use v4 API headers for verification
            headers = self._get_headers(
                include_idempotency=False,  # GET requests don't need idempotency
                include_trace=True
            )
            
            response = requests.get(
                f'{self.base_url}/transactions/{transaction_id}/verify',
                headers=headers,
                timeout=30
            )
            
            # Handle response with error handling
            success, result = self.error_handler.handle_response(response, "Payment verification")
            
            if success:
                data = result['data']
                if data.get('status') == 'success':
                    payment_data = data.get('data', {})
                    
                    return {
                        'success': True,
                        'verified': True,
                        'status': payment_data.get('status'),
                        'amount': payment_data.get('amount'),
                        'currency': payment_data.get('currency'),
                        'data': data
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Verification failed')
                    }
            else:
                # Error response handled by error handler
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message'],
                    'retryable': result['retryable']
                }
                
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_webhook(self, webhook_data, signature):
        """
        Process incoming webhook from Flutterwave
        """
        try:
            # Verify webhook signature
            if not self._verify_webhook_signature(webhook_data, signature):
                return {
                    'success': False,
                    'error': 'Invalid webhook signature'
                }
            
            # Parse webhook data
            event_type = webhook_data.get('event')
            payment_data = webhook_data.get('data', {})
            
            # Find transaction by reference
            reference = payment_data.get('tx_ref')
            if not reference:
                return {
                    'success': False,
                    'error': 'No transaction reference found'
                }
            
            from .models import PaymentTransaction, PaymentWebhook
            
            try:
                transaction = PaymentTransaction.objects.get(reference=reference)
            except PaymentTransaction.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Transaction not found: {reference}'
                }
            
            # Create webhook record
            webhook = PaymentWebhook.objects.create(
                webhook_id=f"WEBHOOK-{timezone.now().strftime('%Y%m%d')}-{transaction.reference}",
                transaction=transaction,
                event_type=event_type,
                webhook_data=webhook_data
            )
            
            # Process based on event type
            if event_type == 'charge.completed':
                return self._handle_payment_success(transaction, payment_data, webhook)
            elif event_type == 'charge.failed':
                return self._handle_payment_failed(transaction, payment_data, webhook)
            elif event_type == 'transfer.completed':
                return self._handle_transfer_completed(transaction, payment_data, webhook)
            else:
                webhook.processed = True
                webhook.processed_at = timezone.now()
                webhook.save()
                
                return {
                    'success': True,
                    'message': f'Webhook processed: {event_type}'
                }
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _verify_webhook_signature(self, webhook_data, signature):
        """
        Verify webhook signature from Flutterwave
        """
        try:
            # Get the secret hash from settings
            secret_hash = getattr(settings, 'FLUTTERWAVE_SECRET_HASH', '')
            if not secret_hash:
                logger.warning("Flutterwave secret hash not configured")
                return True  # Skip verification if not configured
            
            # Create expected signature
            expected_signature = hmac.new(
                secret_hash.encode(),
                json.dumps(webhook_data, separators=(',', ':')).encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    def _handle_payment_success(self, transaction, payment_data, webhook):
        """
        Handle successful payment
        """
        try:
            # Update transaction status
            transaction.status = 'successful'
            transaction.paid_at = timezone.now()
            transaction.flutterwave_webhook_data = payment_data
            transaction.save()
            
            # Update related entity based on transaction type
            if transaction.transaction_type == 'order' and transaction.order:
                transaction.order.payment_status = 'paid'
                transaction.order.payment_transaction_id = transaction.transaction_id
                transaction.order.save()
            
            elif transaction.transaction_type == 'invoice' and transaction.invoice:
                transaction.invoice.mark_as_paid()
            
            elif transaction.transaction_type == 'event' and transaction.event:
                # Handle event payment success
                pass
            
            # Mark webhook as processed
            webhook.processed = True
            webhook.processed_at = timezone.now()
            webhook.save()
            
            return {
                'success': True,
                'message': 'Payment processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            webhook.processed = False
            webhook.processing_error = str(e)
            webhook.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_payment_failed(self, transaction, payment_data, webhook):
        """
        Handle failed payment
        """
        try:
            # Update transaction status
            transaction.status = 'failed'
            transaction.flutterwave_webhook_data = payment_data
            transaction.metadata['failure_reason'] = payment_data.get('failure_reason', 'Payment failed')
            transaction.save()
            
            # Mark webhook as processed
            webhook.processed = True
            webhook.processed_at = timezone.now()
            webhook.save()
            
            return {
                'success': True,
                'message': 'Payment failure processed'
            }
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            webhook.processed = False
            webhook.processing_error = str(e)
            webhook.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_transfer_completed(self, transaction, payment_data, webhook):
        """
        Handle transfer completion
        """
        try:
            # Mark webhook as processed
            webhook.processed = True
            webhook.processed_at = timezone.now()
            webhook.save()
            
            return {
                'success': True,
                'message': 'Transfer completed'
            }
            
        except Exception as e:
            logger.error(f"Error handling transfer completion: {e}")
            webhook.processed = False
            webhook.processing_error = str(e)
            webhook.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_refund(self, transaction, amount, reason):
        """
        Create a refund for a transaction
        """
        try:
            payload = {
                'id': transaction.flutterwave_reference,
                'amount': str(amount),
                'reason': reason
            }
            
            response = requests.post(
                f'{self.base_url}/refunds',
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    refund_data = data.get('data', {})
                    
                    from .models import PaymentRefund
                    
                    refund = PaymentRefund.objects.create(
                        original_transaction=transaction,
                        amount=amount,
                        reason=reason,
                        status='successful',
                        flutterwave_response=data
                    )
                    
                    return {
                        'success': True,
                        'refund_id': refund.refund_id,
                        'data': data
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Refund creation failed')
                    }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error creating refund: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_banks(self, country='NG'):
        """
        Get list of banks for bank transfer
        """
        try:
            response = requests.get(
                f'{self.base_url}/banks/{country}',
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'success': True,
                        'banks': data.get('data', [])
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Failed to fetch banks')
                    }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error fetching banks: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_bank_account(self, account_number, account_bank):
        """
        Validate bank account number
        """
        try:
            payload = {
                'account_number': account_number,
                'account_bank': account_bank
            }
            
            response = requests.post(
                f'{self.base_url}/accounts/resolve',
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    account_data = data.get('data', {})
                    return {
                        'success': True,
                        'account_name': account_data.get('account_name'),
                        'data': data
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Account validation failed')
                    }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error validating bank account: {e}")
            return {
                'success': False,
                'error': str(e)
            } 

def update_invoice_status_on_order_payment(order_id):
    """
    Update invoice status to 'paid' when an order is fully paid.
    This service is called when payment transactions are created or updated.
    
    The function:
    1. Gets all successful/paid payment transactions for the order
    2. Calculates total amount paid from transactions
    3. Uses order.total_amount (which includes subtotal + tax + delivery_fee - discount)
    4. Only marks invoices as paid if total_paid >= total_order_amount
    5. Also updates order status from 'pending' to 'confirmed' if fully paid
    """
    from django.db.models import Sum
    from orders.models import Order, Invoice
    from payments.models import PaymentTransaction
    from decimal import Decimal
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get the order
        order = Order.objects.get(id=order_id)
        
        # Get all successful payment transactions for this order
        successful_payments = PaymentTransaction.objects.filter(
            order_id=order_id,
            status__in=['successful', 'paid']
        )
        
        # Calculate total amount paid from payment transactions
        total_paid = successful_payments.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Use the order's total_amount (which is calculated as subtotal + tax + delivery_fee - discount)
        total_order_amount = order.total_amount
        
        # Log the calculation details
        logger.info(f"Order {order.order_number} payment calculation:")
        logger.info(f"  - Total paid: {total_paid}")
        logger.info(f"  - Order total: {total_order_amount}")
        logger.info(f"  - Order subtotal: {order.subtotal}")
        logger.info(f"  - Order tax: {order.tax}")
        logger.info(f"  - Order delivery_fee: {order.delivery_fee}")
        logger.info(f"  - Order discount: {order.discount}")
        
        # Check if order is fully paid
        if total_paid >= total_order_amount:
            # Get all invoices for this order
            invoices = Invoice.objects.filter(order=order)
            
            updated_invoices = 0
            for invoice in invoices:
                if invoice.status != 'paid':
                    # Mark invoice as paid
                    invoice.status = 'paid'
                    invoice.amount_paid = invoice.total_amount
                    invoice.balance_due = 0
                    invoice.outstanding_amount = 0
                    invoice.paid_at = timezone.now()
                    invoice.save()
                    
                    logger.info(f"Invoice {invoice.invoice_number} marked as paid for order {order.order_number}")
                    updated_invoices += 1
            
            # Update order status from 'pending' to 'confirmed' if fully paid
            order_status_updated = False
            if order.status == 'pending':
                order.status = 'confirmed'
                order.payment_status = 'paid'
                order.save()
                order_status_updated = True
                logger.info(f"Order {order.order_number} status updated from 'pending' to 'confirmed'")
            
            if updated_invoices > 0 or order_status_updated:
                logger.info(f"Updated {updated_invoices} invoice(s) and order status for order {order.order_number}")
            
            return {
                'success': True,
                'order_id': order_id,
                'total_paid': total_paid,
                'order_total': order.total_amount,
                'invoices_updated': updated_invoices,
                'order_status_updated': order_status_updated
            }
        else:
            # Order is not fully paid yet
            return {
                'success': True,
                'order_id': order_id,
                'total_paid': total_paid,
                'order_total': order.total_amount,
                'invoices_updated': 0,
                'order_status_updated': False,
                'message': 'Order not fully paid yet'
            }
            
    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} does not exist")
        return {
            'success': False,
            'error': f'Order with ID {order_id} does not exist'
        }
    except Exception as e:
        logger.error(f"Error updating invoice status for order {order_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        } 

def create_receipt_for_successful_payment(payment_transaction):
    """
    Create a receipt for a successful payment transaction.
    This function is called when a payment transaction status changes to 'successful' or 'done'.
    
    Args:
        payment_transaction: PaymentTransaction instance that was successfully completed
        
    Returns:
        dict: Result of the receipt creation process
    """
    from payments.models import PaymentReceipt
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Support receipts for all successful payment transactions (order, invoice, event, standalone)
        order = payment_transaction.order if getattr(payment_transaction, 'order', None) else None
        
        # Idempotency using PaymentReceipt one_to_one to transaction
        existing_receipt = getattr(payment_transaction, 'payment_receipt', None)
        
        # Fallback check for legacy receipts created before tracking_data key was added
        if not existing_receipt:
            existing_receipt = getattr(payment_transaction, 'payment_receipt', None)
        
        if existing_receipt:
            logger.info(f"Receipt already exists for payment transaction {payment_transaction.transaction_id}")
            return {
                'success': True,
                'receipt_created': False,
                'receipt_id': existing_receipt.id,
                'receipt_number': existing_receipt.receipt_number,
                'message': 'Receipt already exists for this payment'
            }
        
        # Create a PaymentReceipt instead of OrderReceipt to decouple from delivery receipts
        # Maintain existing OrderReceipt flow: do NOT auto-create delivery receipt here
        receipt = PaymentReceipt.objects.create(
            transaction=payment_transaction,
            order=order,
            invoice=payment_transaction.invoice if getattr(payment_transaction, 'invoice', None) else None,
            event=payment_transaction.event if getattr(payment_transaction, 'event', None) else None,
            customer_name=payment_transaction.customer_name,
            customer_email=payment_transaction.customer_email,
            customer_phone=payment_transaction.customer_phone,
            amount=payment_transaction.amount,
            currency=payment_transaction.currency,
            payment_method_name=payment_transaction.payment_method.name if payment_transaction.payment_method else None,
            payment_type=payment_transaction.payment_type,
            paid_at=payment_transaction.paid_at or payment_transaction.created_at,
            notes=(
                f"Payment Transaction: {payment_transaction.transaction_id}\n"
                f"Payment Method: {payment_transaction.payment_method.name if payment_transaction.payment_method else 'Unknown'}\n"
                f"Amount Paid: {payment_transaction.amount} {payment_transaction.currency}\n"
                f"Payment Date: {payment_transaction.paid_at or payment_transaction.created_at}"
            ),
            metadata={
                'payment_transaction_id': payment_transaction.id,
                'payment_transaction_reference': payment_transaction.transaction_id,
            }
        )
        
        logger.info(f"Created payment_receipt {receipt.receipt_number} for payment transaction {payment_transaction.transaction_id}")
        
        return {
            'success': True,
            'receipt_created': True,
            'receipt_id': receipt.id,
            'receipt_number': receipt.receipt_number,
            'message': f'Receipt {receipt.receipt_number} created successfully'
        }
        
    except Exception as e:
        logger.error(f"Error creating receipt for payment transaction {payment_transaction.transaction_id}: {str(e)}")
        return {
            'success': False,
            'receipt_created': False,
            'error': str(e)
        } 