from rest_framework import serializers
from .models import InventoryItem, StockMovement
from orders.models import PreOrder, Wishlist


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for InventoryItem model"""
    
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    stock_level_percentage = serializers.FloatField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)
    is_overstocked = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product_id', 'product_name', 'product_sku',
            'current_stock', 'reserved_stock', 'available_stock',
            'min_stock_level', 'max_stock_level', 'reorder_point', 'reorder_quantity',
            'is_active', 'allow_backorders', 'track_quantity',
            'location', 'supplier', 'cost_price',
            'batch_number', 'expiry_date',
            'last_updated', 'last_stock_check',
            'stock_status', 'stock_level_percentage', 'days_until_expiry',
            'is_in_stock', 'is_out_of_stock', 'is_low_stock', 
            'needs_reorder', 'is_overstocked', 'is_expired', 'is_expiring_soon'
        ]
        read_only_fields = ['last_updated', 'last_stock_check']


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    
    product_name = serializers.CharField(source='inventory_item.product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_incoming = serializers.BooleanField(read_only=True)
    is_outgoing = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'inventory_item', 'product_name',
            'movement_type', 'quantity', 'previous_stock', 'new_stock',
            'reference', 'notes',
            'cost_per_unit', 'total_value',
            'created_by', 'created_by_name', 'created_at',
            'is_incoming', 'is_outgoing'
        ]
        read_only_fields = ['created_at']


class PreOrderSerializer(serializers.ModelSerializer):
    """Serializer for PreOrder model"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.current_price', max_digits=10, decimal_places=2, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    can_be_fulfilled = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PreOrder
        fields = [
            'id', 'user', 'user_email', 'product', 'product_name', 'product_price',
            'quantity', 'status', 'reserved_price', 'price_locked',
            'notify_when_available', 'notification_sent',
            'expires_at', 'expected_availability',
            'email_notifications', 'sms_notifications',
            'notes', 'priority',
            'created_at', 'updated_at', 'fulfilled_at',
            'can_be_fulfilled', 'is_expired'
        ]
        read_only_fields = ['created_at', 'updated_at', 'fulfilled_at', 'notification_sent']


class WishlistSerializer(serializers.ModelSerializer):
    """Enhanced Wishlist serializer with notification preferences"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    has_price_drop = serializers.BooleanField(read_only=True)
    price_drop_percentage = serializers.FloatField(read_only=True)
    is_target_price_met = serializers.BooleanField(read_only=True)
    should_trigger_price_alert = serializers.BooleanField(read_only=True)
    should_trigger_stock_alert = serializers.BooleanField(read_only=True)
    product_in_stock = serializers.BooleanField(source='product.is_available', read_only=True)

    def get_product_image(self, obj):
        """Safely get product image URL"""
        if obj.product and obj.product.image:
            try:
                return obj.product.image.url
            except (ValueError, AttributeError):
                return None
        return None

    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'product', 'product_name', 'product_image',
            'price_drop_alerts', 'stock_alerts', 'target_price',
            'original_price', 'last_notified_price', 'current_price',
            'was_in_stock', 'last_stock_check', 'product_in_stock',
            'created_at', 'updated_at',
            'has_price_drop', 'price_drop_percentage', 'is_target_price_met',
            'should_trigger_price_alert', 'should_trigger_stock_alert'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_stock_check', 'last_notified_price']


class InventorySummarySerializer(serializers.Serializer):
    """Serializer for inventory summary data"""
    
    total_items = serializers.IntegerField()
    in_stock = serializers.IntegerField()
    low_stock = serializers.IntegerField()
    out_of_stock = serializers.IntegerField()
    need_reorder = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    expired = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    
class StockReservationSerializer(serializers.Serializer):
    """Serializer for stock reservation requests"""
    
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(max_length=100, required=False)
    
    def validate(self, data):
        """Validate stock reservation request"""
        try:
            from .models import Product
            product = Product.objects.get(id=data['product_id'])
            inventory = getattr(product, 'inventory', None)
            
            if not inventory:
                raise serializers.ValidationError("Product inventory not found")
            
            if not inventory.can_reserve(data['quantity']):
                raise serializers.ValidationError(
                    f"Insufficient stock. Available: {inventory.available_stock}, Requested: {data['quantity']}"
                )
                
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        return data


class StockUpdateSerializer(serializers.Serializer):
    """Serializer for stock update requests"""
    
    product_id = serializers.IntegerField()
    new_stock = serializers.IntegerField(min_value=0)
    movement_type = serializers.ChoiceField(choices=StockMovement.MOVEMENT_TYPES, default='adjustment')
    reference = serializers.CharField(max_length=100, required=False)
    notes = serializers.CharField(required=False)
    cost_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    
    def validate(self, data):
        """Validate stock update request"""
        try:
            from .models import Product
            Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        return data


class ProductFilterSerializer(serializers.Serializer):
    """Serializer for advanced product filtering"""
    
    search_query = serializers.CharField(required=False)
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    price_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    price_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    alcohol_min = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    alcohol_max = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    regions = serializers.ListField(child=serializers.CharField(), required=False)
    brands = serializers.ListField(child=serializers.CharField(), required=False)
    vintages = serializers.ListField(child=serializers.CharField(), required=False)
    rating_min = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    rating_max = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    in_stock_only = serializers.BooleanField(default=False)
    on_sale_only = serializers.BooleanField(default=False)
    new_arrivals_only = serializers.BooleanField(default=False)
    sort_by = serializers.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('name_asc', 'Name: A to Z'),
            ('name_desc', 'Name: Z to A'),
            ('rating_desc', 'Rating: High to Low'),
            ('newest_first', 'Newest First'),
            ('oldest_first', 'Oldest First'),
            ('popularity_desc', 'Most Popular'),
        ],
        default='relevance'
    )
