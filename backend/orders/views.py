from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

from .models import Order, OrderItem, Cart, CartItem, Wishlist, Review, OrderReceipt, Invoice
from .serializers import (
    OrderSerializer, OrderDetailSerializer, OrderCreateSerializer, OrderUpdateSerializer,
    OrderItemSerializer, CartSerializer, CartItemSerializer, CartItemCreateSerializer,
    CartItemUpdateSerializer, WishlistSerializer, ReviewSerializer, ReviewCreateSerializer,
    OrderStatsSerializer, OrderFilterSerializer, OrderReceiptSerializer, OrderReceiptDetailSerializer,
    OrderReceiptCreateSerializer, OrderReceiptUpdateSerializer, InvoiceSerializer, InvoiceCreateSerializer,
    InvoiceDetailSerializer, InvoicePaymentSerializer, InvoiceStatsSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for order management
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['orders'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def partial_update(self, request, *args, **kwargs):
        """Update order with enhanced status validation"""
        try:
            order = self.get_object()
            print(f"Partial update request for order {order.order_number}")
            print(f"Request data: {request.data}")
            
            # Check if status is being updated
            if 'status' in request.data:
                new_status = request.data['status']
                print(f"Status update requested: {order.status} -> {new_status}")
                
                # Validate status transition
                if not order.can_transition_to(new_status):
                    print(f"Invalid transition: {order.status} -> {new_status}")
                    return Response(
                        {
                            'error': f'Invalid status transition from {order.status} to {new_status}',
                            'current_status': order.status,
                            'valid_transitions': order.can_transition_to.__closure__[0].cell_contents.get(order.status, [])
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Use the model's update_status method
                try:
                    print(f"Calling update_status: {order.status} -> {new_status}")
                    order.update_status(new_status, user=request.user)
                    print(f"Status updated successfully: {order.status}")
                    # Return the updated order
                    serializer = self.get_serializer(order)
                    return Response(serializer.data)
                except ValueError as e:
                    print(f"ValueError in update_status: {str(e)}")
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Continue with normal partial update for non-status changes
            print("Proceeding with normal partial update")
            return super().partial_update(request, *args, **kwargs)
            
        except Exception as e:
            print(f"Exception in partial_update: {str(e)}")
            return Response(
                {'error': f'Failed to update order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(tags=['orders'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """
        Filter orders based on user type and permissions with advanced date filtering
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            logger.warning("User not authenticated")
            return Order.objects.none()
        
        logger.info(f"Processing request for user: {user.email} (type: {user.user_type})")
        
        # Start with base queryset based on user type
        if hasattr(user, 'user_type') and user.user_type == 'web':
            # WebUser is for anonymous access - return no orders
            logger.info("WebUser detected - returning no orders for anonymous access")
            queryset = Order.objects.none()
        elif user.is_customer:
            queryset = Order.objects.filter(customer=user)
            logger.info(f"Customer queryset: {queryset.count()} orders")
        elif user.is_driver:
            queryset = Order.objects.filter(delivery_person=user)
            logger.info(f"Driver queryset: {queryset.count()} orders")
        elif user.is_admin_user:
            queryset = Order.objects.all()
            logger.info(f"Admin queryset: {queryset.count()} orders")
        else:
            logger.warning(f"Unknown user type: {user.user_type}")
            queryset = Order.objects.none()
        
        # Apply date filtering
        queryset = self._apply_date_filters(queryset)
        
        logger.info(f"Final queryset count: {queryset.count()}")
        return queryset
    
    def _apply_date_filters(self, queryset):
        """
        Apply date filtering based on query parameters
        """
        from datetime import datetime, timedelta
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get date filter parameters
        date_filter = self.request.query_params.get('date_filter', '')
        start_date = self.request.query_params.get('start_date', '')
        end_date = self.request.query_params.get('end_date', '')
        specific_date = self.request.query_params.get('specific_date', '')
        
        # Debug logging
        logger.info(f"Date filter parameters received: date_filter='{date_filter}', start_date='{start_date}', end_date='{end_date}', specific_date='{specific_date}'")
        logger.info(f"All query params: {dict(self.request.query_params)}")
        
        # Apply specific date filter
        if specific_date:
            try:
                date_obj = datetime.strptime(specific_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date=date_obj)
                logger.info(f"Applied specific date filter: {date_obj}")
            except ValueError as e:
                logger.error(f"Invalid specific_date format: {specific_date}, error: {e}")
                pass
        
        # Apply date range filter
        elif start_date and end_date:
            try:
                start_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__range=[start_obj, end_obj])
                logger.info(f"Applied date range filter: {start_obj} to {end_obj}")
            except ValueError as e:
                logger.error(f"Invalid date range format: start_date='{start_date}', end_date='{end_date}', error: {e}")
                pass
        
        # Apply predefined date filters
        elif date_filter:
            now = timezone.now()
            logger.info(f"Applying predefined date filter: {date_filter}")
            
            if date_filter == 'today':
                queryset = queryset.filter(created_at__date=now.date())
                logger.info(f"Applied today filter: {now.date()}")
            elif date_filter == 'yesterday':
                yesterday = now.date() - timedelta(days=1)
                queryset = queryset.filter(created_at__date=yesterday)
                logger.info(f"Applied yesterday filter: {yesterday}")
            elif date_filter == 'week':
                week_ago = now.date() - timedelta(days=7)
                queryset = queryset.filter(created_at__date__gte=week_ago)
                logger.info(f"Applied week filter: >= {week_ago}")
            elif date_filter == 'month':
                month_ago = now.date() - timedelta(days=30)
                queryset = queryset.filter(created_at__date__gte=month_ago)
                logger.info(f"Applied month filter: >= {month_ago}")
            elif date_filter == 'year':
                year_ago = now.date() - timedelta(days=365)
                queryset = queryset.filter(created_at__date__gte=year_ago)
                logger.info(f"Applied year filter: >= {year_ago}")
            elif date_filter == 'this_week':
                # Get start of current week (Monday)
                days_since_monday = now.weekday()
                start_of_week = now.date() - timedelta(days=days_since_monday)
                queryset = queryset.filter(created_at__date__gte=start_of_week)
                logger.info(f"Applied this_week filter: >= {start_of_week}")
            elif date_filter == 'this_month':
                # Get start of current month
                start_of_month = now.date().replace(day=1)
                queryset = queryset.filter(created_at__date__gte=start_of_month)
                logger.info(f"Applied this_month filter: >= {start_of_month}")
            elif date_filter == 'this_year':
                # Get start of current year
                start_of_year = now.date().replace(month=1, day=1)
                queryset = queryset.filter(created_at__date__gte=start_of_year)
                logger.info(f"Applied this_year filter: >= {start_of_year}")
            else:
                logger.warning(f"Unknown date_filter value: {date_filter}")
        
        logger.info(f"Final queryset count after date filtering: {queryset.count()}")
        return queryset
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get current user's orders"
    )
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get current user's orders"""
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Cancel an order"
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        if not order.can_be_cancelled:
            return Response(
                {'error': 'Order cannot be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cancellation_reason = request.data.get('reason', 'Cancelled by customer')
        order.status = 'cancelled'
        order.cancellation_reason = cancellation_reason
        order.save()
        
        # Restore product stock
        for item in order.items.all():
            item.product.update_stock(item.quantity)
        
        return Response({'message': 'Order cancelled successfully'})
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Confirm an order (admin only)"
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an order (admin only)"""
        if not request.user.is_admin_user:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        order.status = 'confirmed'
        order.save()
        
        return Response({'message': 'Order confirmed successfully'})
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Assign a driver to an order (admin only)"
    )
    @action(detail=True, methods=['post'])
    def assign_driver(self, request, pk=None):
        """Assign a driver to an order (admin only)"""
        if not request.user.is_admin_user:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        driver_id = request.data.get('driver_id')
        
        try:
            from users.models import User
            driver = User.objects.get(id=driver_id, user_type='driver')
            order.delivery_person = driver
            order.delivery_person_name = driver.full_name
            order.delivery_person_phone = driver.phone_number
            order.save()
            
            return Response({'message': 'Driver assigned successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Driver not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get order statistics"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics - accessible to all authenticated users"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        today = timezone.now().date()
        
        # Get order counts
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        
        # Get revenue
        total_revenue = Order.objects.filter(
            status='delivered', 
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        avg_order_value = Order.objects.filter(
            status='delivered'
        ).aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Calculate conversion rate (simplified)
        conversion_rate = 0
        if total_orders > 0:
            conversion_rate = (completed_orders / total_orders) * 100
        
        stats = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'conversion_rate': conversion_rate,
        }
        
        serializer = OrderStatsSerializer(stats)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get basic order statistics for all users"
    )
    @action(detail=False, methods=['get'])
    def basic_stats(self, request):
        """Get basic order statistics - accessible to all authenticated users"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get basic order counts
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        
        # Get basic revenue
        total_revenue = Order.objects.filter(
            status='delivered', 
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        basic_stats = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_revenue': total_revenue,
        }
        
        return Response(basic_stats)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get order payment balance"
    )
    @action(detail=True, methods=['get'])
    def payment_balance(self, request, pk=None):
        """Get payment balance for an order"""
        try:
            order = self.get_object()
            
            # Get successful payment transactions for this order
            from payments.models import PaymentTransaction
            successful_payments = PaymentTransaction.objects.filter(
                order=order,
                status='successful'
            )
            
            # Calculate total paid amount
            total_paid = successful_payments.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Calculate balance
            order_total = float(order.total_amount)
            balance = order_total - float(total_paid)
            
            # Determine if order is fully paid
            is_fully_paid = balance <= 0
            is_partially_paid = total_paid > 0 and balance > 0
            
            data = {
                'order_id': order.id,
                'order_number': order.order_number,
                'order_total': order_total,
                'total_paid': float(total_paid),
                'balance': balance,
                'is_fully_paid': is_fully_paid,
                'is_partially_paid': is_partially_paid,
                'payment_transactions_count': successful_payments.count(),
                'payment_transactions': [
                    {
                        'id': payment.id,
                        'amount': float(payment.amount),
                        'status': payment.status,
                        'created_at': payment.created_at.isoformat(),
                        'payment_method': payment.payment_method.name if payment.payment_method else None
                    }
                    for payment in successful_payments
                ]
            }
            
            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get payment balance: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for cart management
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['orders'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get current user's cart"
    )
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Get current user's cart"""
        user = request.user
        
        # Handle WebUser - return empty cart for anonymous access
        if hasattr(user, 'user_type') and user.user_type == 'web':
            logger.info("WebUser detected - returning empty cart for anonymous access")
            return Response({
                'id': None,
                'user': None,
                'items': [],
                'total_items': 0,
                'total_amount': 0,
                'created_at': None,
                'updated_at': None
            })
        
        # For authenticated users, get or create cart
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Add item to cart"
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        serializer = CartItemCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            cart_item = serializer.save()
            return Response(CartItemSerializer(cart_item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Update cart item quantity"
    )
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update cart item quantity"""
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(
                id=item_id, 
                cart__user=request.user
            )
            
            if quantity <= 0:
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            else:
                cart_item.quantity = quantity
                cart_item.save()
                return Response(CartItemSerializer(cart_item).data)
                
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Remove item from cart"
    )
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(
                id=item_id, 
                cart__user=request.user
            )
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Clear all items from cart"
    )
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'})
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Checkout cart and create order"
    )
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Checkout cart and create order"""
        user = request.user
        
        # Handle WebUser - return error for anonymous checkout
        if hasattr(user, 'user_type') and user.user_type == 'web':
            logger.info("WebUser detected - checkout not allowed for anonymous users")
            return Response(
                {'error': 'Checkout requires user authentication. Please sign in to complete your order.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cart items and prepare order data
        cart_items = cart.items.all()
        logger.info(f"Processing checkout for user {user.email} with {cart_items.count()} items")
        
        # Create order data with proper structure
        order_data = {
            'items': [
                {
                    'product_id': item.product.id,
                    'quantity': item.quantity
                }
                for item in cart_items
            ],
            'customer_name': getattr(user, 'full_name', user.email),
            'customer_email': user.email,
            'customer_phone': getattr(user, 'phone_number', ''),
            'payment_method': request.data.get('payment_method', 'mobile_money'),
            'is_pickup': request.data.get('is_pickup', False),
            'delivery_address': request.data.get('delivery_address', ''),
            'delivery_instructions': request.data.get('delivery_instructions', ''),
            'delivery_fee': request.data.get('delivery_fee', 0),
            'notes': request.data.get('notes', '')
        }
        
        logger.info(f"Order data prepared: {order_data}")
        
        # Create order using serializer
        serializer = OrderCreateSerializer(data=order_data, context={'request': request})
        if serializer.is_valid():
            try:
                order = serializer.save()
                logger.info(f"Order created successfully: {order.order_number}")
                
                # Clear cart after successful order creation
                cart.items.all().delete()
                logger.info(f"Cart cleared for user {user.email}")
                
                return Response({
                    'message': 'Order created successfully',
                    'order': OrderSerializer(order).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                return Response(
                    {'error': f'Failed to create order: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            logger.error(f"Order serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for wishlist management
    """
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Allow web token auth for read operations, require Firebase auth for write operations"""
        if self.action in ['list', 'retrieve']:
            # Allow web token authentication for reading
            return []
        return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(tags=['orders'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(tags=['orders'])
    def list(self, request, *args, **kwargs):
        """List wishlist items - allows web token auth for reading"""
        # For web token authentication, return sample data
        if hasattr(request.user, 'username') and request.user.username == 'web_user':
            # Return the existing wishlist item for demonstration
            wishlist_items = Wishlist.objects.all()[:5]  # Limit to 5 items for demo
            serializer = self.get_serializer(wishlist_items, many=True)
            return Response({
                'count': wishlist_items.count(),
                'results': serializer.data
            })
        
        # For Firebase authentication, return user's wishlist
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Add item to wishlist"""
        product_id = request.data.get('product')
        
        # Check if already in wishlist
        if Wishlist.objects.filter(user=request.user, product_id=product_id).exists():
            return Response(
                {'error': 'Product already in wishlist'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Add wishlist item to cart"
    )
    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """Add wishlist item to cart"""
        wishlist_id = request.data.get('wishlist_id')
        
        try:
            wishlist_item = Wishlist.objects.get(
                id=wishlist_id, 
                user=request.user
            )
            
            # Add to cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=wishlist_item.product,
                defaults={'quantity': 1}
            )
            
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            
            return Response({'message': 'Item added to cart'})
            
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Wishlist item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for review management
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['orders'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'product')
        
        # Filter by product
        product = self.request.query_params.get('product', None)
        if product:
            queryset = queryset.filter(product_id=product)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        max_rating = self.request.query_params.get('max_rating', None)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        if max_rating:
            queryset = queryset.filter(rating__lte=max_rating)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a review"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(
                user=request.user,
                product=serializer.validated_data['product']
            ).first()
            
            if existing_review:
                return Response(
                    {'error': 'You have already reviewed this product'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            review = serializer.save()
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get current user's reviews"
    )
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews"""
        reviews = Review.objects.filter(user=request.user).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class OrderReceiptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for order receipt management
    """
    queryset = OrderReceipt.objects.all()
    serializer_class = OrderReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['orders'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderReceiptCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return OrderReceiptDetailSerializer
        return OrderReceiptSerializer
    
    def get_queryset(self):
        """
        Filter receipts based on user type and permissions
        """
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return OrderReceipt.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return OrderReceipt.objects.none()
            
        if user.is_customer:
            return OrderReceipt.objects.filter(order__customer=user)
        elif user.is_driver:
            return OrderReceipt.objects.filter(delivery_person=user)
        elif user.is_admin_user:
            return OrderReceipt.objects.all()
        else:
            return OrderReceipt.objects.none()
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get current user's receipts"
    )
    @action(detail=False, methods=['get'])
    def my_receipts(self, request):
        """Get current user's receipts"""
        if request.user.is_customer:
            receipts = OrderReceipt.objects.filter(order__customer=request.user).order_by('-created_at')
        elif request.user.is_driver:
            receipts = OrderReceipt.objects.filter(delivery_person=request.user).order_by('-created_at')
        else:
            receipts = OrderReceipt.objects.all().order_by('-created_at')
        
        serializer = OrderReceiptSerializer(receipts, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Send receipt to customer"
    )
    @action(detail=True, methods=['post'])
    def send_to_customer(self, request, pk=None):
        """Send receipt to customer"""
        receipt = self.get_object()
        
        if receipt.send_to_customer():
            serializer = OrderReceiptSerializer(receipt)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Receipt cannot be sent in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Sign receipt by customer"
    )
    @action(detail=True, methods=['post'])
    def sign_by_customer(self, request, pk=None):
        """Sign receipt by customer"""
        receipt = self.get_object()
        
        signature_data = request.data.get('signature')
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        
        if not signature_data:
            return Response(
                {'error': 'Signature data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if receipt.sign_by_customer(signature_data, ip_address, user_agent):
            serializer = OrderReceiptSerializer(receipt)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Receipt cannot be signed in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Mark receipt as delivered"
    )
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark receipt as delivered"""
        receipt = self.get_object()
        
        if receipt.mark_delivered():
            serializer = OrderReceiptSerializer(receipt)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Receipt cannot be marked as delivered in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for invoice management
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['orders'])
    def list(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Invoice list request from user: {request.user.email}")
        response = super().list(request, *args, **kwargs)
        logger.info(f"Invoice list response count: {len(response.data.get('results', []))}")
        return response
    
    @swagger_auto_schema(tags=['orders'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['orders'])
    def destroy(self, request, *args, **kwargs):
        """Delete an invoice"""
        try:
            invoice = self.get_object()
            invoice_number = invoice.invoice_number
            invoice.delete()
            return Response({
                'success': True,
                'message': f'Invoice {invoice_number} deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to delete invoice: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return InvoiceDetailSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        """
        Filter invoices based on user type and permissions
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Invoice.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            logger.warning("User not authenticated for invoice access")
            return Invoice.objects.none()
        
        logger.info(f"Processing invoice request for user: {user.email} (type: {user.user_type})")
        
        if user.is_customer:
            queryset = Invoice.objects.filter(order__customer=user)
            logger.info(f"Customer invoice queryset: {queryset.count()} invoices")
        elif user.is_driver:
            queryset = Invoice.objects.filter(order__delivery_person=user)
            logger.info(f"Driver invoice queryset: {queryset.count()} invoices")
        elif user.is_admin_user:
            queryset = Invoice.objects.all()
            logger.info(f"Admin invoice queryset: {queryset.count()} invoices")
        else:
            logger.warning(f"Unknown user type for invoice access: {user.user_type}")
            return Invoice.objects.none()
        
        logger.info(f"Final invoice queryset count: {queryset.count()}")
        return queryset

    @swagger_auto_schema(tags=['orders'])
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download branded invoice PDF"""
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from django.conf import settings
        invoice = self.get_object()

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Branding (needed for watermark and header)
        company = getattr(settings, 'SITE_NAME', 'Company')
        address = getattr(settings, 'SITE_ADDRESS', '')
        email = getattr(settings, 'SITE_EMAIL', '')
        phone = getattr(settings, 'SITE_PHONE', '')
        logo_path = getattr(settings, 'SITE_LOGO_PATH', '')
        logo_url = getattr(settings, 'SITE_LOGO_URL', '')

        # Watermark
        try:
            from reportlab.lib.utils import ImageReader
            wm_src = None
            if logo_path:
                wm_src = ImageReader(logo_path)
            elif logo_url:
                wm_src = ImageReader(logo_url)
            if wm_src:
                p.saveState()
                try:
                    p.setFillAlpha(0.08)
                except Exception:
                    pass
                wm_w_target = width * 0.6
                wm_h_target = height * 0.6
                p.drawImage(wm_src, (width - wm_w_target) / 2, (height - wm_h_target) / 2,
                            width=wm_w_target, height=wm_h_target,
                            preserveAspectRatio=True, mask='auto')
                p.restoreState()
        except Exception:
            pass

        # Header band
        p.setFillColorRGB(0.95, 0.95, 0.95)
        p.rect(0, height - 90, width, 90, stroke=0, fill=1)
        p.setFillColor(colors.black)

        # Logo (scaled to fit within 110x50 while preserving aspect ratio)
        def _draw_header_logo(img_src):
            try:
                iw, ih = img_src.getSize()
                target_w, target_h = 110.0, 50.0
                scale = min(target_w / float(iw), target_h / float(ih))
                draw_w, draw_h = iw * scale, ih * scale
                p.drawImage(
                    img_src,
                    40,
                    height - 80,  # baseline area for the band
                    width=draw_w,
                    height=draw_h,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception:
                pass

        if logo_path or logo_url:
            try:
                from reportlab.lib.utils import ImageReader
                img_src = ImageReader(logo_path) if logo_path else ImageReader(logo_url)
                _draw_header_logo(img_src)
            except Exception:
                # best-effort; ignore if not drawable
                pass

        # Company details
        y = height - 35
        p.setFont('Helvetica-Bold', 18)
        p.drawString(150, y, company)
        p.setFont('Helvetica', 9)
        y -= 14
        if address:
            p.drawString(150, y, address)
            y -= 12
        if email or phone:
            p.drawString(150, y, f"{email}{'  |  ' if email and phone else ''}{phone}")

        # Invoice meta
        p.setFont('Helvetica-Bold', 16)
        p.drawRightString(width - 40, height - 35, 'Invoice')
        p.setFont('Helvetica', 10)
        p.drawRightString(width - 40, height - 50, f"Invoice #: {invoice.invoice_number}")
        if getattr(invoice, 'created_at', None):
            p.drawRightString(width - 40, height - 64, f"Date: {invoice.created_at.strftime('%Y-%m-%d %H:%M')}")
        if getattr(invoice, 'due_date', None):
            p.drawRightString(width - 40, height - 78, f"Due: {invoice.due_date.strftime('%Y-%m-%d %H:%M')}")

        # Divider
        p.setStrokeColorRGB(0.85, 0.85, 0.85)
        p.setLineWidth(1)
        p.line(40, height - 100, width - 40, height - 100)

        # Bill to
        y = height - 130
        p.setFont('Helvetica-Bold', 12)
        p.drawString(40, y, 'Bill To')
        p.setFont('Helvetica', 10)
        y -= 16
        p.drawString(40, y, f"{invoice.customer_name}")
        y -= 14
        p.drawString(40, y, f"{invoice.customer_email}")
        if getattr(invoice, 'customer_phone', None):
            y -= 14
            p.drawString(40, y, f"{invoice.customer_phone}")

        # Summary (no line items detail available here)
        y -= 28
        p.setFont('Helvetica-Bold', 11)
        p.drawRightString(width - 120, y, 'Subtotal:')
        p.setFont('Helvetica', 10)
        p.drawRightString(width - 40, y, f"{invoice.subtotal}")
        y -= 14
        p.setFont('Helvetica-Bold', 11)
        p.drawRightString(width - 120, y, 'Tax:')
        p.setFont('Helvetica', 10)
        p.drawRightString(width - 40, y, f"{invoice.tax_amount}")
        y -= 14
        p.setFont('Helvetica-Bold', 11)
        p.drawRightString(width - 120, y, 'Delivery:')
        p.setFont('Helvetica', 10)
        p.drawRightString(width - 40, y, f"{invoice.delivery_fee}")
        y -= 14
        p.setFont('Helvetica-Bold', 11)
        p.drawRightString(width - 120, y, 'Discount:')
        p.setFont('Helvetica', 10)
        p.drawRightString(width - 40, y, f"{invoice.discount_amount}")
        y -= 16
        p.setFont('Helvetica-Bold', 12)
        p.drawRightString(width - 120, y, 'Total:')
        p.setFont('Helvetica-Bold', 12)
        p.drawRightString(width - 40, y, f"{invoice.total_amount}")

        # Footer
        p.setStrokeColorRGB(0.9, 0.9, 0.9)
        p.line(40, 60, width - 40, 60)
        p.setFont('Helvetica', 9)
        p.setFillColor(colors.grey)
        p.drawCentredString(width / 2, 45, f"Thank you for your business • {company}")

        p.save()
        buffer.seek(0)
        from django.http import HttpResponse
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
        return response
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get current user's invoices"
    )
    @action(detail=False, methods=['get'])
    def my_invoices(self, request):
        """Get current user's invoices"""
        if request.user.is_customer:
            invoices = Invoice.objects.filter(order__customer=request.user).order_by('-created_at')
        elif request.user.is_driver:
            invoices = Invoice.objects.filter(order__delivery_person=request.user).order_by('-created_at')
        else:
            invoices = Invoice.objects.all().order_by('-created_at')
        
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Send invoice to customer"
    )
    @action(detail=True, methods=['post'])
    def send_invoice(self, request, pk=None):
        """Send invoice to customer"""
        invoice = self.get_object()
        
        if not invoice.can_be_sent:
            return Response(
                {'error': 'Invoice cannot be sent'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice.send_invoice()
            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to send invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Apply payment to invoice"
    )
    @action(detail=True, methods=['post'])
    def apply_payment(self, request, pk=None):
        """Apply payment to invoice"""
        invoice = self.get_object()
        serializer = InvoicePaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                amount = serializer.validated_data['amount']
                payment_method = serializer.validated_data.get('payment_method')
                transaction_id = serializer.validated_data.get('transaction_id')
                
                invoice.apply_payment(amount, payment_method, transaction_id)
                serializer = InvoiceSerializer(invoice)
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {'error': f'Failed to apply payment: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Mark invoice as paid"
    )
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        
        if not invoice.can_be_paid:
            return Response(
                {'error': 'Invoice cannot be marked as paid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment_method = request.data.get('payment_method')
            transaction_id = request.data.get('transaction_id')
            invoice.mark_as_paid(payment_method, transaction_id)
            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to mark invoice as paid: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Cancel invoice"
    )
    @action(detail=True, methods=['post'])
    def cancel_invoice(self, request, pk=None):
        """Cancel invoice"""
        invoice = self.get_object()
        
        if invoice.status not in ['draft', 'sent']:
            return Response(
                {'error': 'Invoice cannot be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice.cancel_invoice()
            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to cancel invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        tags=['orders'],
        operation_description="Get invoice statistics"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get invoice statistics"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get invoice counts
        total_invoices = Invoice.objects.count()
        draft_invoices = Invoice.objects.filter(status='draft').count()
        sent_invoices = Invoice.objects.filter(status='sent').count()
        paid_invoices = Invoice.objects.filter(status='paid').count()
        overdue_invoices = Invoice.objects.filter(status='overdue').count()
        
        # Get amounts
        total_amount = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = Invoice.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
        total_outstanding = Invoice.objects.filter(status__in=['sent', 'overdue']).aggregate(
            total=Sum('balance_due')
        )['total'] or 0
        
        stats = {
            'total_invoices': total_invoices,
            'draft_invoices': draft_invoices,
            'sent_invoices': sent_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_invoices,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding,
        }
        
        serializer = InvoiceStatsSerializer(stats)
        return Response(serializer.data)


class DeliveryTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for delivery tracking based on orders
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return orders that are deliverable (not pickup)"""
        if hasattr(self.request.user, 'username') and self.request.user.username == 'web_user':
            # For web token auth, return sample data
            return Order.objects.none()
        return Order.objects.filter(
            is_pickup=False,
            status__in=['confirmed', 'processing', 'ready_for_delivery', 'out_for_delivery', 'delivered']
        ).filter(customer=self.request.user)
    
    def get_permissions(self):
        """Allow web token auth for read operations"""
        if self.action in ['list', 'retrieve', 'track_by_order_number']:
            return []
        return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(
        tags=['delivery-tracking'],
        operation_description="Get delivery statistics for the current user"
    )
    @action(detail=False, methods=['get'])
    def delivery_stats(self, request):
        """Get delivery statistics for the current user"""
        if hasattr(request.user, 'username') and request.user.username == 'web_user':
            # Return sample data for web token authentication
            sample_data = {
                'total_deliveries': 3,
                'pending': 1,
                'processing': 1,
                'out_for_delivery': 1,
                'delivered': 0,
                'cancelled': 0
            }
            return Response(sample_data)
        
        # For Firebase authentication, calculate real stats
        user_orders = Order.objects.filter(
            customer=request.user,
            is_pickup=False
        )
        
        stats = {
            'total_deliveries': user_orders.count(),
            'pending': user_orders.filter(status='confirmed').count(),
            'processing': user_orders.filter(status='processing').count(),
            'out_for_delivery': user_orders.filter(status='out_for_delivery').count(),
            'delivered': user_orders.filter(status='delivered').count(),
            'cancelled': user_orders.filter(status='cancelled').count()
        }
        
        return Response(stats)
    
    @swagger_auto_schema(
        tags=['delivery-tracking'],
        operation_description="Get active deliveries for the current user"
    )
    @action(detail=False, methods=['get'])
    def active_deliveries(self, request):
        """Get active deliveries for the current user"""
        if hasattr(request.user, 'username') and request.user.username == 'web_user':
            # Return sample data for web token authentication
            sample_data = [
                {
                    'id': 1,
                    'order_number': 'ORD-2024-001',
                    'status': 'out_for_delivery',
                    'delivery_address': '123 Main Street, Kampala',
                    'delivery_instructions': 'Ring doorbell twice',
                    'estimated_delivery_time': timezone.now().isoformat(),
                    'total_amount': '24990.00',
                    'delivery_fee': '2000.00'
                },
                {
                    'id': 2,
                    'order_number': 'ORD-2024-002',
                    'status': 'processing',
                    'delivery_address': '456 Oak Avenue, Kampala',
                    'delivery_instructions': 'Leave at front desk',
                    'estimated_delivery_time': timezone.now().isoformat(),
                    'total_amount': '399.00',
                    'delivery_fee': '1500.00'
                }
            ]
            return Response(sample_data)
        
        # For Firebase authentication, return real active deliveries
        active_orders = Order.objects.filter(
            customer=request.user,
            is_pickup=False,
            status__in=['confirmed', 'processing', 'ready_for_delivery', 'out_for_delivery']
        ).order_by('-created_at')
        
        serializer = OrderSerializer(active_orders, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['delivery-tracking'],
        operation_description="Track delivery by order number"
    )
    @action(detail=False, methods=['get'])
    def track_by_order_number(self, request):
        """Track delivery by order number"""
        order_number = request.query_params.get('order_number')
        if not order_number:
            return Response(
                {'error': 'Order number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if hasattr(request.user, 'username') and request.user.username == 'web_user':
            # Return sample data for web token authentication
            sample_data = {
                'id': 1,
                'order_number': order_number,
                'status': 'out_for_delivery',
                'delivery_address': '123 Main Street, Kampala',
                'delivery_instructions': 'Ring doorbell twice',
                'estimated_delivery_time': timezone.now().isoformat(),
                'actual_delivery_time': None,
                'delivery_person_name': 'John Driver',
                'delivery_person_phone': '+256123456789',
                'total_amount': '24990.00',
                'delivery_fee': '2000.00',
                'created_at': timezone.now().isoformat(),
                'updated_at': timezone.now().isoformat()
            }
            return Response(sample_data)
        
        # For Firebase authentication, find actual order
        try:
            order = Order.objects.get(
                order_number=order_number,
                is_pickup=False
            )
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        tags=['delivery-tracking'],
        operation_description="Get all deliverable orders with delivery instructions"
    )
    @action(detail=False, methods=['get'])
    def deliverable_orders(self, request):
        """Get all deliverable orders with delivery instructions"""
        if hasattr(request.user, 'username') and request.user.username == 'web_user':
            # Return sample data for web token authentication
            sample_data = [
                {
                    'id': 1,
                    'order_number': 'ORD-2024-001',
                    'status': 'out_for_delivery',
                    'delivery_address': '123 Main Street, Kampala',
                    'delivery_instructions': 'Ring doorbell twice',
                    'estimated_delivery_time': timezone.now().isoformat(),
                    'total_amount': '24990.00',
                    'delivery_fee': '2000.00',
                    'created_at': timezone.now().isoformat()
                },
                {
                    'id': 2,
                    'order_number': 'ORD-2024-002',
                    'status': 'processing',
                    'delivery_address': '456 Oak Avenue, Kampala',
                    'delivery_instructions': 'Leave at front desk',
                    'estimated_delivery_time': timezone.now().isoformat(),
                    'total_amount': '399.00',
                    'delivery_fee': '1500.00',
                    'created_at': timezone.now().isoformat()
                }
            ]
            return Response(sample_data)
        
        # For Firebase authentication, return real deliverable orders
        deliverable_orders = Order.objects.filter(
            customer=request.user,
            is_pickup=False,
            status__in=['confirmed', 'processing', 'ready_for_delivery', 'out_for_delivery', 'delivered']
        ).order_by('-created_at')
        
        serializer = OrderSerializer(deliverable_orders, many=True)
        return Response(serializer.data)
