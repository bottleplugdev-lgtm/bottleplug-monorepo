from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid

from .models import (
    PaymentMethod, PaymentTransaction, PaymentWebhook, 
    PaymentRefund, PaymentPlan, PaymentSubscription
)
from .serializers import (
    PaymentMethodSerializer, PaymentTransactionSerializer, PaymentTransactionDetailSerializer,
    PaymentTransactionCreateSerializer, PaymentWebhookSerializer as WebhookModelSerializer,
    PaymentRefundSerializer, PaymentRefundCreateSerializer, PaymentPlanSerializer,
    PaymentSubscriptionSerializer, PaymentSubscriptionCreateSerializer,
    PaymentInitiateSerializer, PaymentVerifySerializer, PaymentWebhookSerializer,
    BankAccountValidationSerializer, PaymentStatsSerializer, PaymentReceiptSerializer
)
from .services import FlutterwaveService
from users.authentication import FirebaseAuthentication


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment methods
    """
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        FirebaseAuthentication,
        SessionAuthentication,
    ]
    
    @swagger_auto_schema(tags=['payments'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Get payment methods by country"
    )
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get payment methods by country"""
        country = request.query_params.get('country', 'NG')
        methods = self.queryset.filter(country_code=country)
        serializer = self.get_serializer(methods, many=True)
        return Response(serializer.data)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment transactions
    """
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        FirebaseAuthentication,
        SessionAuthentication,
    ]
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return PaymentTransactionDetailSerializer
        elif self.action == 'create':
            return PaymentTransactionCreateSerializer
        return PaymentTransactionSerializer
    
    def get_queryset(self):
        """
        Filter transactions based on user type and permissions
        """
        if getattr(self, 'swagger_fake_view', False):
            return PaymentTransaction.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return PaymentTransaction.objects.none()
            
        if user.is_customer:
            return PaymentTransaction.objects.filter(customer=user)
        elif user.is_driver:
            return PaymentTransaction.objects.filter(
                Q(order__delivery_person=user) | 
                Q(invoice__order__delivery_person=user)
            )
        elif user.is_admin_user:
            return PaymentTransaction.objects.all()
        else:
            return PaymentTransaction.objects.none()
    
    @swagger_auto_schema(tags=['payments'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Initiate a new payment"
    )
    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        """Initiate a new payment"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"DEBUG: Received payment data: {request.data}")
        
        serializer = PaymentInitiateSerializer(data=request.data)
        if serializer.is_valid():
            logger.info(f"DEBUG: Serializer is valid, validated data: {serializer.validated_data}")
            try:
                # Create transaction
                amount = serializer.validated_data['amount']
                transaction_data = {
                    'transaction_type': serializer.validated_data['transaction_type'],
                    'amount': amount,
                    'currency': serializer.validated_data['currency'],
                    'customer': request.user,
                    'customer_name': request.user.get_full_name() or request.user.email,
                    'customer_email': request.user.email,
                    'customer_phone': getattr(request.user, 'phone', '') or '0000000000',
                    'description': serializer.validated_data.get('description', ''),
                    'redirect_url': serializer.validated_data.get('redirect_url', ''),
                    'callback_url': serializer.validated_data.get('callback_url', ''),
                    'metadata': serializer.validated_data.get('metadata', {}),
                    'net_amount': amount  # Set net_amount to amount initially (fees will be calculated later)
                }
                
                # Add payment details to metadata if provided
                if serializer.validated_data.get('payment_details'):
                    if 'metadata' not in transaction_data:
                        transaction_data['metadata'] = {}
                    transaction_data['metadata']['payment_details'] = serializer.validated_data['payment_details']
                
                # Link to related entity
                if serializer.validated_data.get('order_id'):
                    from orders.models import Order
                    try:
                        transaction_data['order'] = Order.objects.get(id=serializer.validated_data['order_id'])
                    except Order.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Order with ID {serializer.validated_data["order_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif serializer.validated_data.get('invoice_id'):
                    from orders.models import Invoice
                    try:
                        transaction_data['invoice'] = Invoice.objects.get(id=serializer.validated_data['invoice_id'])
                    except Invoice.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Invoice with ID {serializer.validated_data["invoice_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif serializer.validated_data.get('event_id'):
                    from events.models import Event
                    try:
                        transaction_data['event'] = Event.objects.get(id=serializer.validated_data['event_id'])
                    except Event.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Event with ID {serializer.validated_data["event_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif serializer.validated_data.get('receipt_id'):
                    from orders.models import OrderReceipt
                    try:
                        transaction_data['receipt'] = OrderReceipt.objects.get(id=serializer.validated_data['receipt_id'])
                    except OrderReceipt.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Receipt with ID {serializer.validated_data["receipt_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Set payment method if provided
                if serializer.validated_data.get('payment_method_id'):
                    try:
                        payment_method = PaymentMethod.objects.get(id=serializer.validated_data['payment_method_id'])
                        transaction_data['payment_method'] = payment_method
                        
                        # Handle cash payments differently - no Flutterwave needed
                        if payment_method.payment_type == 'cash':
                            # For cash payments, create transaction and mark as successful immediately
                            transaction = PaymentTransaction.objects.create(**transaction_data)
                            transaction.status = 'successful'
                            transaction.paid_at = timezone.now()
                            transaction.save()
                            
                            return Response({
                                'success': True,
                                'transaction': PaymentTransactionSerializer(transaction).data,
                                'payment_url': None,
                                'message': 'Cash payment confirmed. Order will be processed for delivery.'
                            })
                    except PaymentMethod.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Payment method with ID {serializer.validated_data["payment_method_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # For non-cash payments, create transaction and then create Flutterwave payment link
                transaction = PaymentTransaction.objects.create(**transaction_data)
                
                # Create payment link with Flutterwave
                flutterwave_service = FlutterwaveService()
                
                result = flutterwave_service.create_payment_link(transaction)
                
                if result['success']:
                    serializer = PaymentTransactionSerializer(transaction)
                    return Response({
                        'success': True,
                        'transaction': serializer.data,
                        'payment_url': result['payment_url']
                    })
                else:
                    transaction.delete()
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Verify payment status"
    )
    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        """Verify payment status"""
        transaction = self.get_object()
        
        try:
            flutterwave_service = FlutterwaveService()
            result = flutterwave_service.verify_payment(transaction.flutterwave_reference)
            
            if result['success'] and result['verified']:
                if result['status'] == 'successful':
                    transaction.mark_as_paid()
                
                serializer = PaymentTransactionSerializer(transaction)
                return Response({
                    'success': True,
                    'transaction': serializer.data,
                    'verification': result
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Payment verification failed')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Get user's payment transactions"
    )
    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """Get user's payment transactions"""
        transactions = PaymentTransaction.objects.filter(customer=request.user).order_by('-created_at')
        serializer = PaymentTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Get payment statistics"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payment statistics"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get transaction counts
        total_transactions = PaymentTransaction.objects.count()
        successful_transactions = PaymentTransaction.objects.filter(status__in=['successful', 'paid']).count()
        failed_transactions = PaymentTransaction.objects.filter(status='failed').count()
        pending_transactions = PaymentTransaction.objects.filter(status='pending').count()
        
        # Get amounts
        total_amount = PaymentTransaction.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_fees = PaymentTransaction.objects.aggregate(total=Sum('fee'))['total'] or 0
        net_amount = PaymentTransaction.objects.aggregate(total=Sum('net_amount'))['total'] or 0
        
        # Get refunds
        refunds_count = PaymentRefund.objects.count()
        refunds_amount = PaymentRefund.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        stats = {
            'total_transactions': total_transactions,
            'successful_transactions': successful_transactions,
            'failed_transactions': failed_transactions,
            'pending_transactions': pending_transactions,
            'total_amount': total_amount,
            'total_fees': total_fees,
            'net_amount': net_amount,
            'refunds_count': refunds_count,
            'refunds_amount': refunds_amount,
        }
        
        serializer = PaymentStatsSerializer(stats)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Check for expired payments and update their status"
    )
    @action(detail=False, methods=['post'])
    def check_expired_payments(self, request):
        """Check for expired payments and update their status"""
        try:
            from django.core.management import call_command
            
            # Check if user has admin permissions
            if not request.user.is_staff:
                return Response(
                    {'error': 'Admin permissions required'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Call the management command
            call_command('check_expired_payments')
            
            return Response({
                'success': True,
                'message': 'Expired payments check completed'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Check payment status for an order"
    )
    @action(detail=False, methods=['get'])
    def order_payment_status(self, request):
        """Check if an order has been fully paid"""
        order_id = request.query_params.get('order_id')
        
        if not order_id:
            return Response({
                'success': False,
                'error': 'order_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get all successful payment transactions for this order
            successful_transactions = PaymentTransaction.objects.filter(
                order_id=order_id,
                status__in=['successful', 'paid']
            )
            
            # Calculate total amount paid
            total_paid = successful_transactions.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Get the order to check its total amount
            from orders.models import Order
            try:
                order = Order.objects.get(id=order_id)
                order_total = float(order.total_amount)
            except Order.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Order not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if payment is complete
            is_paid = total_paid >= order_total
            
            return Response({
                'success': True,
                'order_id': order_id,
                'total_paid': total_paid,
                'order_total': order_total,
                'is_paid': is_paid,
                'payment_status': 'paid' if is_paid else 'pending',
                'transactions_count': successful_transactions.count()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error checking payment status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Check if user has paid for a specific event",
        manual_parameters=[
            openapi.Parameter(
                'event_id',
                openapi.IN_QUERY,
                description="Event ID to check payment for",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def event_payment_status(self, request):
        """Check if user has paid for a specific event"""
        event_id = request.query_params.get('event_id')
        
        if not event_id:
            return Response({
                'success': False,
                'error': 'event_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get all successful payment transactions for this event and user
            successful_transactions = PaymentTransaction.objects.filter(
                event_id=event_id,
                customer=request.user,
                status__in=['successful', 'paid']
            )
            
            # Check if there are any successful payments
            has_paid = successful_transactions.exists()
            
            # Calculate total amount paid for this event
            total_paid = successful_transactions.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            return Response({
                'success': True,
                'event_id': int(event_id),
                'has_paid': has_paid,
                'total_paid': total_paid,
                'transactions_count': successful_transactions.count(),
                'transactions': PaymentTransactionSerializer(successful_transactions, many=True).data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error checking event payment status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Check Flutterwave authentication status"
    )
    @action(detail=False, methods=['get'])
    def auth_status(self, request):
        """Check Flutterwave authentication status"""
        try:
            from .services import FlutterwaveService
            
            # Check if user has admin permissions
            if not request.user.is_staff:
                return Response(
                    {'error': 'Admin permissions required'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Initialize service to check auth status
            flutterwave_service = FlutterwaveService()
            auth_info = flutterwave_service.auth_manager.get_token_info()
            
            return Response({
                'success': True,
                'oauth_configured': auth_info['is_oauth_configured'],
                'has_token': auth_info['has_token'],
                'token_type': auth_info['token_type'],
                'expires_at': auth_info['expires_at'],
                'time_until_expiry': auth_info['time_until_expiry'],
                'using_oauth': auth_info['is_oauth_configured'] and auth_info['has_token'],
                'environment': flutterwave_service.environment,
                'base_url': flutterwave_service.base_url
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Test payment initiation (no auth required)"
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def test_initiate_payment(self, request):
        """Test payment initiation without authentication"""
        serializer = PaymentInitiateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Get the first user for testing
                from django.contrib.auth import get_user_model
                User = get_user_model()
                test_user = User.objects.first()
                
                if not test_user:
                    return Response({
                        'success': False,
                        'error': 'No users found in database'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create transaction data
                transaction_data = {
                    'transaction_id': f"TXN-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
                    'reference': f"REF-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
                    'transaction_type': serializer.validated_data['transaction_type'],
                    'amount': serializer.validated_data['amount'],
                    'currency': serializer.validated_data['currency'],
                    'customer': test_user,
                    'customer_name': test_user.get_full_name() or test_user.email,
                    'customer_email': test_user.email,
                    'description': serializer.validated_data.get('description', 'Test payment'),
                    'status': 'pending'
                }
                
                # Add payment details if provided
                if serializer.validated_data.get('payment_details'):
                    if 'metadata' not in transaction_data:
                        transaction_data['metadata'] = {}
                    transaction_data['metadata']['payment_details'] = serializer.validated_data['payment_details']
                
                # Link to related entity
                if serializer.validated_data.get('order_id'):
                    from orders.models import Order
                    try:
                        transaction_data['order'] = Order.objects.get(id=serializer.validated_data['order_id'])
                    except Order.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Order with ID {serializer.validated_data["order_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif serializer.validated_data.get('invoice_id'):
                    from orders.models import Invoice
                    try:
                        transaction_data['invoice'] = Invoice.objects.get(id=serializer.validated_data['invoice_id'])
                    except Invoice.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Invoice with ID {serializer.validated_data["invoice_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif serializer.validated_data.get('event_id'):
                    from events.models import Event
                    try:
                        transaction_data['event'] = Event.objects.get(id=serializer.validated_data['event_id'])
                    except Event.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Event with ID {serializer.validated_data["event_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif serializer.validated_data.get('receipt_id'):
                    from orders.models import OrderReceipt
                    try:
                        transaction_data['receipt'] = OrderReceipt.objects.get(id=serializer.validated_data['receipt_id'])
                    except OrderReceipt.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Receipt with ID {serializer.validated_data["receipt_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Set payment method if provided
                if serializer.validated_data.get('payment_method_id'):
                    try:
                        transaction_data['payment_method'] = PaymentMethod.objects.get(id=serializer.validated_data['payment_method_id'])
                    except PaymentMethod.DoesNotExist:
                        return Response({
                            'success': False,
                            'error': f'Payment method with ID {serializer.validated_data["payment_method_id"]} does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                transaction = PaymentTransaction.objects.create(**transaction_data)
                
                # Handle cash payments differently
                if transaction.payment_method and transaction.payment_method.payment_type == 'cash':
                    # For cash payments, mark as successful immediately
                    transaction.status = 'successful'
                    transaction.paid_at = timezone.now()
                    transaction.save()
                    
                    return Response({
                        'success': True,
                        'transaction': PaymentTransactionSerializer(transaction).data,
                        'payment_url': None,
                        'message': 'Cash payment confirmed. Order will be processed for delivery.'
                    })
                
                # For other payment methods, return success without Flutterwave
                return Response({
                    'success': True,
                    'transaction': PaymentTransactionSerializer(transaction).data,
                    'payment_url': 'https://flutterwave.com/pay/test',
                    'message': 'Payment initiated successfully (test mode)'
                })
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Get payments by order ID and status"
    )
    @action(detail=False, methods=['get'])
    def by_order(self, request):
        """Get payments for a specific order with optional status filter"""
        order_id = request.query_params.get('order_id')
        status = request.query_params.get('status', 'successful')
        
        if not order_id:
            return Response({
                'success': False,
                'error': 'order_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Filter payments by order_id and status
            payments = self.get_queryset().filter(
                order_id=order_id,
                status=status
            )
            
            # Use the basic serializer for list view
            serializer = PaymentTransactionSerializer(payments, many=True)
            
            # Calculate total paid amount
            total_paid = sum(payment.amount for payment in payments)
            
            return Response({
                'success': True,
                'order_id': order_id,
                'status': status,
                'total_paid': total_paid,
                'payment_count': len(payments),
                'payments': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentWebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment webhooks
    """
    queryset = PaymentWebhook.objects.all()
    serializer_class = WebhookModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['payments'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Process Flutterwave webhook"
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def flutterwave_webhook(self, request):
        """Process Flutterwave webhook"""
        try:
            # Get webhook data
            webhook_data = request.data
            signature = request.headers.get('verif-hash', '')
            
            # Process webhook
            flutterwave_service = FlutterwaveService()
            result = flutterwave_service.process_webhook(webhook_data, signature)
            
            if result['success']:
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentRefundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment refunds
    """
    queryset = PaymentRefund.objects.all()
    serializer_class = PaymentRefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentRefundCreateSerializer
        return PaymentRefundSerializer
    
    @swagger_auto_schema(tags=['payments'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Create refund via Flutterwave"
    )
    @action(detail=False, methods=['post'])
    def create_flutterwave_refund(self, request):
        """Create refund via Flutterwave"""
        serializer = PaymentRefundCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get original transaction
                transaction = PaymentTransaction.objects.get(
                    id=serializer.validated_data['original_transaction'].id
                )
                
                # Create refund with Flutterwave
                flutterwave_service = FlutterwaveService()
                result = flutterwave_service.create_refund(
                    transaction,
                    serializer.validated_data['amount'],
                    serializer.validated_data['reason']
                )
                
                if result['success']:
                    refund = PaymentRefund.objects.get(refund_id=result['refund_id'])
                    serializer = PaymentRefundSerializer(refund)
                    return Response({
                        'success': True,
                        'refund': serializer.data
                    })
                else:
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for payment receipts"""
    from .serializers import PaymentReceiptSerializer
    from .models import PaymentReceipt
    queryset = PaymentReceipt.objects.all()
    serializer_class = PaymentReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        FirebaseAuthentication,
        SessionAuthentication,
    ]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.queryset.none()
        if user.is_admin_user:
            return self._apply_filters(self.queryset)
        # Customers: their own payment receipts via transaction.customer
        return self._apply_filters(self.queryset.filter(transaction__customer=user))

    def _apply_filters(self, qs):
        """Apply optional filters: transaction_id, reference, date_from, date_to, amount_min, amount_max"""
        params = self.request.query_params
        tx_id = params.get('transaction_id')
        reference = params.get('reference')
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        amount_min = params.get('amount_min')
        amount_max = params.get('amount_max')

        if tx_id:
            qs = qs.filter(transaction__transaction_id=tx_id)
        if reference:
            qs = qs.filter(transaction__reference=reference)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if amount_min:
            qs = qs.filter(amount__gte=amount_min)
        if amount_max:
            qs = qs.filter(amount__lte=amount_max)
        return qs

    @swagger_auto_schema(tags=['payments'])
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download payment receipt as PDF with branding"""
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from django.conf import settings
        receipt = self.get_object()

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Company branding settings (needed for watermark and header)
        company = getattr(settings, 'SITE_NAME', 'Company')
        address = getattr(settings, 'SITE_ADDRESS', '')
        email = getattr(settings, 'SITE_EMAIL', '')
        phone = getattr(settings, 'SITE_PHONE', '')
        logo_url = getattr(settings, 'SITE_LOGO_URL', '')
        logo_path = getattr(settings, 'SITE_LOGO_PATH', '')

        # Watermark (draw first so other content sits on top)
        wm_drawn = False
        try:
            from reportlab.lib.utils import ImageReader
            wm_src = None
            if logo_path:
                wm_src = ImageReader(logo_path)
            elif logo_url:
                wm_src = ImageReader(logo_url)
            if wm_src:
                p.saveState()
                # Transparency (if supported)
                try:
                    p.setFillAlpha(0.08)
                except Exception:
                    pass
                # Scale watermark to ~50% page width preserving aspect ratio
                iw, ih = wm_src.getSize()
                wm_w_target = width * 0.5
                scale = wm_w_target / float(iw)
                wm_h_target = ih * scale
                # Draw centered
                p.drawImage(wm_src, (width - wm_w_target) / 2, (height - wm_h_target) / 2,
                            width=wm_w_target, height=wm_h_target,
                            preserveAspectRatio=True, mask='auto')
                p.restoreState()
                wm_drawn = True
        except Exception:
            pass

        # Header band
        p.setFillColorRGB(0.95, 0.95, 0.95)
        p.rect(0, height - 90, width, 90, stroke=0, fill=1)
        p.setFillColor(colors.black)

        y = height - 35
        # Try to draw logo if configured (scaled nicely)
        def _draw_header_logo(img_src):
            try:
                iw, ih = img_src.getSize()
                target_w, target_h = 110.0, 50.0
                scale = min(target_w / float(iw), target_h / float(ih))
                draw_w, draw_h = iw * scale, ih * scale
                p.drawImage(img_src, 40, height - 80, width=draw_w, height=draw_h,
                            preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        if logo_path or logo_url:
            try:
                from reportlab.lib.utils import ImageReader
                img_src = ImageReader(logo_path) if logo_path else ImageReader(logo_url)
                _draw_header_logo(img_src)
            except Exception:
                pass

        p.setFont('Helvetica-Bold', 18)
        p.drawString(150, y, company)
        p.setFont('Helvetica', 9)
        y -= 14
        if address:
            p.drawString(150, y, address)
            y -= 12
        if email or phone:
            p.drawString(150, y, f"{email}{'  |  ' if email and phone else ''}{phone}")

        # Receipt title and meta
        p.setFont('Helvetica-Bold', 16)
        p.drawRightString(width - 40, height - 35, 'Payment Receipt')
        p.setFont('Helvetica', 10)
        p.drawRightString(width - 40, height - 50, f"Receipt #: {receipt.receipt_number}")
        p.drawRightString(width - 40, height - 64, f"Date: {receipt.created_at.strftime('%Y-%m-%d %H:%M')}")

        # Horizontal divider
        p.setStrokeColorRGB(0.85, 0.85, 0.85)
        p.setLineWidth(1)
        p.line(40, height - 100, width - 40, height - 100)

        # Bill to
        y = height - 130
        p.setFont('Helvetica-Bold', 12)
        p.drawString(40, y, 'Bill To')
        p.setFont('Helvetica', 10)
        y -= 16
        p.drawString(40, y, f"{receipt.customer_name}")
        y -= 14
        p.drawString(40, y, f"{receipt.customer_email}")
        if receipt.customer_phone:
            y -= 14
            p.drawString(40, y, f"{receipt.customer_phone}")

        # Payment details box
        y -= 28
        p.setFont('Helvetica-Bold', 12)
        p.drawString(40, y, 'Payment Details')
        y -= 18
        p.setFont('Helvetica', 10)
        p.drawString(50, y, f"Amount Paid:")
        p.setFont('Helvetica-Bold', 12)
        p.drawString(150, y, f"{receipt.amount} {receipt.currency}")
        p.setFont('Helvetica', 10)
        y -= 16
        if receipt.payment_method_name:
            p.drawString(50, y, f"Payment Method: {receipt.payment_method_name}")
            y -= 14
        if receipt.payment_type:
            p.drawString(50, y, f"Payment Type: {receipt.payment_type}")
            y -= 14
        if receipt.paid_at:
            p.drawString(50, y, f"Paid At: {receipt.paid_at.strftime('%Y-%m-%d %H:%M')}")
            y -= 14
        if receipt.order_id:
            p.drawString(50, y, f"Order ID: {receipt.order_id}")
            y -= 14
        if receipt.invoice_id:
            p.drawString(50, y, f"Invoice ID: {receipt.invoice_id}")
            y -= 14
        if receipt.event_id:
            p.drawString(50, y, f"Event ID: {receipt.event_id}")
            y -= 14

        # Notes
        if receipt.notes:
            y -= 12
            p.setFont('Helvetica-Bold', 12)
            p.drawString(40, y, 'Notes')
            y -= 16
            p.setFont('Helvetica', 10)
            for line in str(receipt.notes).split('\n'):
                p.drawString(50, y, line[:110])
                y -= 12
                if y < 60:
                    p.showPage()
                    y = height - 60

        # Footer
        if y < 80:
            p.showPage()
            y = height - 60
        p.setStrokeColorRGB(0.9, 0.9, 0.9)
        p.line(40, 60, width - 40, 60)
        p.setFont('Helvetica', 9)
        p.setFillColor(colors.grey)
        p.drawCentredString(width / 2, 45, f"Thank you for your business • {company}")

        p.save()
        buffer.seek(0)
        from django.http import HttpResponse
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{receipt.receipt_number}.pdf"'
        return response

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Synchronize missing payment_receipts and remove orphans"
    )
    @action(detail=False, methods=['post'])
    def sync_missing(self, request):
        """Trigger backend command to create missing payment_receipts and clean orphans"""
        try:
            # Optional dry_run flag
            dry_run = bool(request.data.get('dry_run', False))

            # Restrict to staff/admin users
            user = request.user
            if not (user and user.is_authenticated and user.is_staff):
                return Response({'error': 'Admin permissions required'}, status=status.HTTP_403_FORBIDDEN)

            from django.core.management import call_command
            from io import StringIO
            import sys

            cmd_args = ['sync_payment_receipts']
            if dry_run:
                cmd_args.append('--dry_run')

            old_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result
            try:
                call_command(*cmd_args)
                output = result.getvalue()
            finally:
                sys.stdout = old_stdout

            return Response({'success': True, 'output': output, 'dry_run': dry_run})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment plans
    """
    queryset = PaymentPlan.objects.filter(is_active=True)
    serializer_class = PaymentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['payments'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class PaymentSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment subscriptions
    """
    queryset = PaymentSubscription.objects.all()
    serializer_class = PaymentSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentSubscriptionCreateSerializer
        return PaymentSubscriptionSerializer
    
    def get_queryset(self):
        """
        Filter subscriptions based on user
        """
        if getattr(self, 'swagger_fake_view', False):
            return PaymentSubscription.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return PaymentSubscription.objects.none()
            
        if user.is_customer:
            return PaymentSubscription.objects.filter(customer=user)
        elif user.is_admin_user:
            return PaymentSubscription.objects.all()
        else:
            return PaymentSubscription.objects.none()
    
    @swagger_auto_schema(tags=['payments'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['payments'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Get user's subscriptions"
    )
    @action(detail=False, methods=['get'])
    def my_subscriptions(self, request):
        """Get user's subscriptions"""
        subscriptions = PaymentSubscription.objects.filter(customer=request.user).order_by('-created_at')
        serializer = PaymentSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class FlutterwaveUtilityViewSet(viewsets.ViewSet):
    """
    ViewSet for Flutterwave utility functions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Get list of banks"
    )
    @action(detail=False, methods=['get'])
    def banks(self, request):
        """Get list of banks"""
        country = request.query_params.get('country', 'NG')
        
        try:
            flutterwave_service = FlutterwaveService()
            result = flutterwave_service.get_banks(country)
            
            if result['success']:
                return Response({
                    'success': True,
                    'banks': result['banks']
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Validate bank account"
    )
    @action(detail=False, methods=['post'])
    def validate_bank_account(self, request):
        """Validate bank account"""
        serializer = BankAccountValidationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                flutterwave_service = FlutterwaveService()
                result = flutterwave_service.validate_bank_account(
                    serializer.validated_data['account_number'],
                    serializer.validated_data['account_bank']
                )
                
                if result['success']:
                    return Response({
                        'success': True,
                        'account_name': result['account_name']
                    })
                else:
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Complete mobile money payment flow (all steps combined)"
    )
    @action(detail=False, methods=['post'])
    def complete_mobile_money_payment(self, request):
        """Complete mobile money payment flow with all Flutterwave steps"""
        try:
            from .mobile_money import FlutterwaveMobileMoney
            
            # Validate required data
            required_fields = ['customer_data', 'mobile_money_data', 'charge_data']
            for field in required_fields:
                if field not in request.data:
                    return Response({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate customer data
            customer_data = request.data.get('customer_data', {})
            if not customer_data.get('email'):
                return Response({
                    'success': False,
                    'error': 'Customer email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate mobile money data
            mobile_money_data = request.data.get('mobile_money_data', {})
            if not mobile_money_data.get('country_code') or not mobile_money_data.get('network') or not mobile_money_data.get('phone_number'):
                return Response({
                    'success': False,
                    'error': 'Mobile money data must include country_code, network, and phone_number'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate charge data
            charge_data = request.data.get('charge_data', {})
            if not charge_data.get('amount') or not charge_data.get('currency'):
                return Response({
                    'success': False,
                    'error': 'Charge data must include amount and currency'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize mobile money service
            mobile_money_service = FlutterwaveMobileMoney()
            
            # Validate country and network
            validation_result = mobile_money_service.validate_country_network(
                mobile_money_data['country_code'],
                mobile_money_data['network']
            )
            
            if not validation_result['valid']:
                return Response({
                    'success': False,
                    'error': validation_result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prepare payment data for complete flow
            payment_data = {
                'customer_data': customer_data,
                'mobile_money_data': mobile_money_data,
                'charge_data': charge_data
            }
            
            # Add scenario if provided (for testing)
            if 'scenario' in request.data:
                payment_data['scenario'] = request.data['scenario']
            
            # Execute complete mobile money flow
            result = mobile_money_service.complete_mobile_money_flow(payment_data)
            
            if result['success']:
                # Create PaymentTransaction record in database
                try:
                    from .models import PaymentTransaction, PaymentMethod
                    
                    # Get or create mobile money payment method
                    payment_method, created = PaymentMethod.objects.get_or_create(
                        payment_type='mobile_money',
                        defaults={
                            'name': f"{mobile_money_data['network'].upper()} Mobile Money",
                            'description': f"{mobile_money_data['network'].upper()} Mobile Money for {mobile_money_data['country_code']}",
                            'is_active': True,
                            'min_amount': 100,
                            'max_amount': 7000000
                        }
                    )
                    
                    # Create transaction record
                    transaction_data = {
                        'customer': request.user,
                        'customer_name': f"{customer_data.get('name', {}).get('first', '')} {customer_data.get('name', {}).get('last', '')}".strip(),
                        'customer_email': customer_data['email'],
                        'customer_phone': mobile_money_data['phone_number'],  # Add customer phone
                        'amount': charge_data['amount'],
                        'currency': charge_data['currency'],
                        'payment_method': payment_method,
                        'transaction_type': 'mobile_money',
                        'status': 'pending',
                        'reference': charge_data['reference'],
                        'flutterwave_reference': charge_data['reference'],
                        'flutterwave_charge_id': result.get('charge_id'),
                        'flutterwave_customer_id': result.get('customer_id'),
                        'flutterwave_payment_method_id': result.get('payment_method_id'),
                        'description': f"Mobile money payment via {mobile_money_data['network'].upper()}",
                        'metadata': {
                            'network': mobile_money_data['network'],
                            'phone_number': mobile_money_data['phone_number'],
                            'country_code': mobile_money_data['country_code'],
                            'flutterwave_response': result
                        }
                    }
                    
                    # Add entity references if provided
                    if 'order_id' in request.data:
                        from orders.models import Order
                        try:
                            order = Order.objects.get(id=request.data['order_id'])
                            transaction_data['order'] = order
                        except Order.DoesNotExist:
                            pass
                    
                    if 'invoice_id' in request.data:
                        from invoices.models import Invoice
                        try:
                            invoice = Invoice.objects.get(id=request.data['invoice_id'])
                            transaction_data['invoice'] = invoice
                        except Invoice.DoesNotExist:
                            pass
                    
                    if 'event_id' in request.data:
                        from events.models import Event
                        try:
                            event = Event.objects.get(id=request.data['event_id'])
                            transaction_data['event'] = event
                        except Event.DoesNotExist:
                            pass
                    
                    if 'receipt_id' in request.data:
                        from receipts.models import OrderReceipt
                        try:
                            receipt = OrderReceipt.objects.get(id=request.data['receipt_id'])
                            transaction_data['receipt'] = receipt
                        except OrderReceipt.DoesNotExist:
                            pass
                    
                    # Create the transaction
                    transaction = PaymentTransaction.objects.create(**transaction_data)
                    
                    return Response({
                        'success': True,
                        'message': result.get('message', 'Mobile money payment flow completed'),
                        'data': {
                            'transaction_id': transaction.id,
                            'customer_id': result.get('customer_id'),
                            'payment_method_id': result.get('payment_method_id'),
                            'charge_id': result.get('charge_id'),
                            'status': result.get('status'),
                            'next_action': result.get('next_action'),
                            'redirect_url': result.get('redirect_url'),
                            'instructions': result.get('instructions'),
                            'note': result.get('note')
                        }
                    })
                    
                except Exception as db_error:
                    # Log the database error but still return the Flutterwave result
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error creating PaymentTransaction record: {db_error}")
                    
                    return Response({
                        'success': True,
                        'message': result.get('message', 'Mobile money payment flow completed (Flutterwave only)'),
                        'warning': 'Payment recorded with Flutterwave but local database record creation failed',
                        'data': {
                            'customer_id': result.get('customer_id'),
                            'payment_method_id': result.get('payment_method_id'),
                            'charge_id': result.get('charge_id'),
                            'status': result.get('status'),
                            'next_action': result.get('next_action'),
                            'redirect_url': result.get('redirect_url'),
                            'instructions': result.get('instructions'),
                            'note': result.get('note')
                        }
                    })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Mobile money payment failed')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Complete card payment flow (all steps combined)"
    )
    @action(detail=False, methods=['post'])
    def complete_card_payment(self, request):
        """Complete card payment flow with all Flutterwave steps"""
        try:
            from .card_payments import FlutterwaveCardPayments
            
            # Validate required data
            required_fields = ['customer_data', 'card_data', 'charge_data']
            for field in required_fields:
                if field not in request.data:
                    return Response({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate customer data
            customer_data = request.data.get('customer_data', {})
            if not customer_data.get('email'):
                return Response({
                    'success': False,
                    'error': 'Customer email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate card data
            card_data = request.data.get('card_data', {})
            required_card_fields = ['encrypted_card_number', 'encrypted_expiry_month', 'encrypted_expiry_year', 'encrypted_cvv', 'nonce']
            for field in required_card_fields:
                if not card_data.get(field):
                    return Response({
                        'success': False,
                        'error': f'Card data must include {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate charge data
            charge_data = request.data.get('charge_data', {})
            if not charge_data.get('amount') or not charge_data.get('currency'):
                return Response({
                    'success': False,
                    'error': 'Charge data must include amount and currency'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize card payments service
            card_payments_service = FlutterwaveCardPayments()
            
            # Prepare payment data for complete flow
            payment_data = {
                'customer_data': customer_data,
                'card_data': card_data,
                'charge_data': charge_data
            }
            
            # Add scenario if provided (for testing)
            if 'scenario' in request.data:
                payment_data['scenario'] = request.data['scenario']
            
            # Execute complete card payment flow
            result = card_payments_service.complete_card_payment_flow(payment_data)
            
            if result['success']:
                # Create PaymentTransaction record in database
                try:
                    from .models import PaymentTransaction, PaymentMethod
                    
                    # Get or create card payment method
                    payment_method, created = PaymentMethod.objects.get_or_create(
                        payment_type='card',
                        defaults={
                            'name': 'Credit/Debit Card',
                            'description': 'Credit and debit card payments',
                            'is_active': True,
                            'min_amount': 100,
                            'max_amount': 1000000
                        }
                    )
                    
                    # Create transaction record
                    transaction_data = {
                        'customer': request.user,
                        'customer_name': f"{customer_data.get('name', {}).get('first', '')} {customer_data.get('name', {}).get('last', '')}".strip(),
                        'customer_email': customer_data['email'],
                        'amount': charge_data['amount'],
                        'currency': charge_data['currency'],
                        'payment_method': payment_method,
                        'transaction_type': 'card',
                        'status': 'pending',
                        'reference': charge_data['reference'],
                        'flutterwave_reference': charge_data['reference'],
                        'flutterwave_charge_id': result.get('charge_id'),
                        'flutterwave_customer_id': result.get('customer_id'),
                        'flutterwave_payment_method_id': result.get('payment_method_id'),
                        'description': 'Card payment',
                        'metadata': {
                            'card_last4': card_data.get('last4', '****'),
                            'card_brand': card_data.get('brand', 'unknown'),
                            'authorization_required': result.get('authorization_required', False),
                            'auth_type': result.get('auth_type'),
                            'flutterwave_response': result
                        }
                    }
                    
                    # Add entity references if provided
                    if 'order_id' in request.data:
                        from orders.models import Order
                        try:
                            order = Order.objects.get(id=request.data['order_id'])
                            transaction_data['order'] = order
                        except Order.DoesNotExist:
                            pass
                    
                    if 'invoice_id' in request.data:
                        from invoices.models import Invoice
                        try:
                            invoice = Invoice.objects.get(id=request.data['invoice_id'])
                            transaction_data['invoice'] = invoice
                        except Invoice.DoesNotExist:
                            pass
                    
                    if 'event_id' in request.data:
                        from events.models import Event
                        try:
                            event = Event.objects.get(id=request.data['event_id'])
                            transaction_data['event'] = event
                        except Event.DoesNotExist:
                            pass
                    
                    if 'receipt_id' in request.data:
                        from receipts.models import OrderReceipt
                        try:
                            receipt = OrderReceipt.objects.get(id=request.data['receipt_id'])
                            transaction_data['receipt'] = receipt
                        except OrderReceipt.DoesNotExist:
                            pass
                    
                    # Create the transaction
                    transaction = PaymentTransaction.objects.create(**transaction_data)
                    
                    return Response({
                        'success': True,
                        'message': result.get('message', 'Card payment flow completed'),
                        'data': {
                            'transaction_id': transaction.id,
                            'customer_id': result.get('customer_id'),
                            'payment_method_id': result.get('payment_method_id'),
                            'charge_id': result.get('charge_id'),
                            'status': result.get('status'),
                            'next_action': result.get('next_action'),
                            'redirect_url': result.get('redirect_url'),
                            'authorization_required': result.get('authorization_required'),
                            'auth_type': result.get('auth_type')
                        }
                    })
                    
                except Exception as db_error:
                    # Log the database error but still return the Flutterwave result
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error creating PaymentTransaction record: {db_error}")
                    
                    return Response({
                        'success': True,
                        'message': result.get('message', 'Card payment flow completed (Flutterwave only)'),
                        'warning': 'Payment recorded with Flutterwave but local database record creation failed',
                        'data': {
                            'customer_id': result.get('customer_id'),
                            'payment_method_id': result.get('payment_method_id'),
                            'charge_id': result.get('charge_id'),
                            'status': result.get('status'),
                            'next_action': result.get('next_action'),
                            'redirect_url': result.get('redirect_url'),
                            'authorization_required': result.get('authorization_required'),
                            'auth_type': result.get('auth_type')
                        }
                    })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Card payment failed')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['payments'],
        operation_description="Update invoice status for orders that are fully paid, update order status from pending to confirmed, and create receipts for successful payments"
    )
    @action(detail=False, methods=['post'])
    def update_invoice_status(self, request):
        """Update invoice status to paid for orders that are fully paid and update order status from pending to confirmed"""
        try:
            from django.core.management import call_command
            from io import StringIO
            import sys
            
            # Check if user has admin permissions
            if not request.user.is_staff:
                return Response(
                    {'error': 'Admin permissions required'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get parameters from request
            order_id = request.data.get('order_id')
            dry_run = request.data.get('dry_run', False)
            create_receipts = request.data.get('create_receipts', True)  # Default to True
            
            # Prepare command arguments
            cmd_args = ['update_invoice_status']
            if order_id:
                cmd_args.extend(['--order-id', str(order_id)])
            if dry_run:
                cmd_args.append('--dry-run')
            if create_receipts:
                cmd_args.append('--create-receipts')
            
            # Capture command output
            old_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result
            
            try:
                # Call the management command
                call_command(*cmd_args)
                output = result.getvalue()
            finally:
                sys.stdout = old_stdout
            
            return Response({
                'success': True,
                'message': 'Invoice, order status, and receipt update completed',
                'output': output,
                'dry_run': dry_run,
                'create_receipts': create_receipts
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
