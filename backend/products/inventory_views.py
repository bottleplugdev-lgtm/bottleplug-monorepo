from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from decimal import Decimal

from .models import InventoryItem, StockMovement, Product
from orders.models import PreOrder, Wishlist
from .inventory_serializers import (
    InventoryItemSerializer, StockMovementSerializer, PreOrderSerializer,
    WishlistSerializer, InventorySummarySerializer, StockReservationSerializer,
    StockUpdateSerializer, ProductFilterSerializer
)
from .serializers import ProductSerializer
from utils.pagination import PreserveStatePagination


class InventoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inventory management
    """
    queryset = InventoryItem.objects.select_related('product').all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PreserveStatePagination
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'update_stock']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = self.queryset
        
        # Filter by stock status
        status_filter = self.request.query_params.get('status')
        if status_filter == 'low_stock':
            queryset = queryset.filter(available_stock__lte=F('min_stock_level'))
        elif status_filter == 'out_of_stock':
            queryset = queryset.filter(available_stock=0)
        elif status_filter == 'need_reorder':
            queryset = queryset.filter(available_stock__lte=F('reorder_point'))
        elif status_filter == 'expiring_soon':
            thirty_days_from_now = timezone.now() + timezone.timedelta(days=30)
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lte=thirty_days_from_now,
                expiry_date__gt=timezone.now()
            )
        elif status_filter == 'expired':
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lte=timezone.now()
            )
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by supplier
        supplier = self.request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier__icontains=supplier)
        
        return queryset.order_by('-last_updated')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get inventory summary statistics"""
        queryset = self.get_queryset()
        
        summary_data = {
            'total_items': queryset.count(),
            'in_stock': queryset.filter(available_stock__gt=0).count(),
            'low_stock': queryset.filter(available_stock__lte=F('min_stock_level')).count(),
            'out_of_stock': queryset.filter(available_stock=0).count(),
            'need_reorder': queryset.filter(available_stock__lte=F('reorder_point')).count(),
            'expiring_soon': queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lte=timezone.now() + timezone.timedelta(days=30),
                expiry_date__gt=timezone.now()
            ).count(),
            'expired': queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lte=timezone.now()
            ).count(),
            'total_value': queryset.aggregate(
                total=Sum(F('current_stock') * F('cost_price'))
            )['total'] or Decimal('0')
        }
        
        serializer = InventorySummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reserve(self, request):
        """Reserve stock for an order"""
        serializer = StockReservationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                product = Product.objects.get(id=serializer.validated_data['product_id'])
                inventory = getattr(product, 'inventory', None)
                
                if not inventory:
                    return Response(
                        {'error': 'Product inventory not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                success = inventory.reserve_stock(
                    serializer.validated_data['quantity'],
                    serializer.validated_data.get('reference')
                )
                
                if success:
                    return Response({
                        'success': True,
                        'message': f"Reserved {serializer.validated_data['quantity']} units",
                        'available_stock': inventory.available_stock
                    })
                else:
                    return Response(
                        {'error': 'Failed to reserve stock'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def release(self, request):
        """Release reserved stock"""
        serializer = StockReservationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                product = Product.objects.get(id=serializer.validated_data['product_id'])
                inventory = getattr(product, 'inventory', None)
                
                if not inventory:
                    return Response(
                        {'error': 'Product inventory not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                released_qty = inventory.release_stock(
                    serializer.validated_data['quantity'],
                    serializer.validated_data.get('reference')
                )
                
                return Response({
                    'success': True,
                    'message': f"Released {released_qty} units",
                    'available_stock': inventory.available_stock
                })
                    
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_stock(self, request):
        """Update stock level"""
        serializer = StockUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                product = Product.objects.get(id=serializer.validated_data['product_id'])
                inventory, created = InventoryItem.objects.get_or_create(
                    product=product,
                    defaults={
                        'current_stock': 0,
                        'available_stock': 0
                    }
                )
                
                quantity_change = inventory.update_stock(
                    serializer.validated_data['new_stock'],
                    serializer.validated_data.get('movement_type', 'adjustment'),
                    serializer.validated_data.get('reference'),
                    serializer.validated_data.get('notes')
                )
                
                return Response({
                    'success': True,
                    'message': f"Stock updated by {quantity_change} units",
                    'current_stock': inventory.current_stock,
                    'available_stock': inventory.available_stock
                })
                    
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for stock movement history
    """
    queryset = StockMovement.objects.select_related('inventory_item__product', 'created_by').all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PreserveStatePagination
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = self.queryset
        
        # Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(inventory_item__product_id=product_id)
        
        # Filter by movement type
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')


class PreOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for pre-order management
    """
    queryset = PreOrder.objects.select_related('user', 'product').all()
    serializer_class = PreOrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PreserveStatePagination
    
    def get_queryset(self):
        """Filter queryset based on user and query parameters"""
        queryset = self.queryset
        
        # Filter by user for non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset.order_by('-priority', '-created_at')
    
    def perform_create(self, serializer):
        """Set user and default expiry when creating pre-order"""
        pre_order = serializer.save(user=self.request.user)
        pre_order.set_expiry(days=30)  # Default 30-day expiry
        
        # Lock price if product is available
        if pre_order.product.is_available:
            pre_order.lock_price()
    
    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        """Fulfill a pre-order"""
        pre_order = self.get_object()
        
        if pre_order.fulfill():
            return Response({
                'success': True,
                'message': 'Pre-order fulfilled successfully'
            })
        else:
            return Response(
                {'error': 'Cannot fulfill pre-order'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a pre-order"""
        pre_order = self.get_object()
        reason = request.data.get('reason', 'Cancelled by user')
        
        pre_order.cancel(reason)
        return Response({
            'success': True,
            'message': 'Pre-order cancelled successfully'
        })


class EnhancedWishlistViewSet(viewsets.ModelViewSet):
    """
    Enhanced ViewSet for wishlist with notification preferences
    """
    queryset = Wishlist.objects.select_related('user', 'product').all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PreserveStatePagination
    
    def get_queryset(self):
        """Filter queryset by user"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user and initialize price tracking when creating wishlist item"""
        wishlist_item = serializer.save(user=self.request.user)
        wishlist_item.update_price_tracking()
        wishlist_item.update_stock_tracking()
    
    @action(detail=True, methods=['post'])
    def update_notifications(self, request, pk=None):
        """Update notification preferences for wishlist item"""
        wishlist_item = self.get_object()
        
        price_drop_alerts = request.data.get('price_drop_alerts')
        stock_alerts = request.data.get('stock_alerts')
        target_price = request.data.get('target_price')
        
        if price_drop_alerts is not None:
            wishlist_item.price_drop_alerts = price_drop_alerts
        if stock_alerts is not None:
            wishlist_item.stock_alerts = stock_alerts
        if target_price is not None:
            wishlist_item.target_price = target_price
        
        wishlist_item.save()
        
        serializer = self.get_serializer(wishlist_item)
        return Response(serializer.data)
