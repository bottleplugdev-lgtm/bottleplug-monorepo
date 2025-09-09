from rest_framework import serializers
from .models import Category, Product, ProductVariant, ProductImage, InventoryLog, ProductMeasurement


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    product_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'parent', 'is_active',
            'sort_order', 'product_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating categories"""
    
    class Meta:
        model = Category
        fields = [
            'name', 'description', 'image', 'parent', 'is_active', 'sort_order'
        ]
    
    def validate_name(self, value):
        """Validate that the category name is unique"""
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(f"A category with the name '{value}' already exists.")
        return value
    
    def validate_parent(self, value):
        """Validate parent category"""
        if value and not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Parent category does not exist.")
        return value


class ProductMeasurementSerializer(serializers.ModelSerializer):
    """Serializer for ProductMeasurement model"""
    measurement_display = serializers.CharField(source='get_measurement_display', read_only=True)
    display_name = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductMeasurement
        fields = [
            'id', 'measurement', 'measurement_display', 'quantity', 'price', 
            'original_price', 'is_active', 'is_default', 'sort_order',
            'display_name', 'is_on_sale', 'discount_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductMeasurementCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating product measurements"""
    
    product = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ProductMeasurement
        fields = [
            'measurement', 'quantity', 'price', 'original_price',
            'is_active', 'is_default', 'sort_order', 'product'
        ]
    
    def validate(self, data):
        """Validate measurement data"""
        # Get product from context (for create) or from instance (for update)
        product = self.context.get('product')
        if not product and self.instance:
            product = self.instance.product
        
        if product:
            # Check for duplicate measurement and quantity combination
            existing = ProductMeasurement.objects.filter(
                product=product,
                measurement=data['measurement'],
                quantity=data.get('quantity')
            )
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            
            if existing.exists():
                raise serializers.ValidationError(
                    f"A measurement with '{data['measurement']}' and quantity '{data.get('quantity')}' already exists for this product."
                )
        
        return data


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model"""
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'sku', 'price', 'stock', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model"""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'is_primary', 'sort_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """Basic Product serializer"""
    category = CategorySerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    measurements = ProductMeasurementSerializer(many=True, read_only=True)
    current_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name', 'subcategory',
            'sku', 'status', 'price', 'original_price', 'sale_percentage', 'unit',
            'stock', 'image', 'is_featured', 'is_new', 'is_on_sale', 'average_rating',
            'review_count', 'created_at', 'updated_at', 'variants', 'images', 
            'measurements', 'current_price'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed Product serializer with all fields"""
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    measurements = ProductMeasurementSerializer(many=True, read_only=True)
    current_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'subcategory', 'sku', 'status',
            'price', 'original_price', 'sale_percentage', 'unit', 'stock',
            'min_stock_level', 'max_stock_level', 'vintage', 'region',
            'alcohol_percentage', 'volume', 'image', 'images', 'is_featured',
            'is_new', 'is_on_sale', 'average_rating', 'review_count', 'tags',
            'pairings', 'awards', 'bulk_pricing', 'variants', 'measurements',
            'current_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products"""
    measurements = ProductMeasurementCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'subcategory', 'sku', 'status',
            'price', 'original_price', 'sale_percentage', 'unit', 'stock',
            'min_stock_level', 'max_stock_level', 'vintage', 'region',
            'alcohol_percentage', 'volume', 'image', 'images', 'is_featured',
            'is_new', 'is_on_sale', 'tags', 'pairings', 'awards', 'bulk_pricing',
            'measurements'
        ]
    
    def validate_category(self, value):
        """Validate that the category exists"""
        if value and not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Selected category does not exist.")
        return value
    
    def create(self, validated_data):
        measurements_data = validated_data.pop('measurements', [])
        product = Product.objects.create(**validated_data)
        
        # Create measurements
        for measurement_data in measurements_data:
            ProductMeasurement.objects.create(product=product, **measurement_data)
        
        # If no measurements provided, create a default one using legacy fields
        if not measurements_data and (validated_data.get('price') or validated_data.get('unit')):
            ProductMeasurement.objects.create(
                product=product,
                measurement=validated_data.get('unit', 'piece'),
                price=validated_data.get('price', 0),
                original_price=validated_data.get('original_price'),
                stock=validated_data.get('stock', 0),
                is_default=True
            )
        
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products"""
    measurements = ProductMeasurementCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'subcategory', 'status',
            'price', 'original_price', 'sale_percentage', 'unit', 'stock',
            'min_stock_level', 'max_stock_level', 'vintage', 'region',
            'alcohol_percentage', 'volume', 'image', 'images', 'is_featured',
            'is_new', 'is_on_sale', 'tags', 'pairings', 'awards', 'bulk_pricing',
            'measurements'
        ]
    
    def update(self, instance, validated_data):
        measurements_data = validated_data.pop('measurements', None)
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update measurements if provided
        if measurements_data is not None:
            # Delete existing measurements
            instance.measurements.all().delete()
            
            # Create new measurements
            for measurement_data in measurements_data:
                ProductMeasurement.objects.create(product=instance, **measurement_data)
        
        return instance


class InventoryLogSerializer(serializers.ModelSerializer):
    """Serializer for InventoryLog model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    measurement_display = serializers.CharField(source='measurement.display_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = InventoryLog
        fields = [
            'id', 'product', 'product_name', 'measurement', 'measurement_display',
            'log_type', 'quantity', 'previous_stock', 'new_stock', 'reference', 
            'notes', 'created_by', 'created_by_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search"""
    query = serializers.CharField(max_length=200, required=False)
    category = serializers.CharField(max_length=100, required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    status = serializers.CharField(max_length=20, required=False)
    measurement = serializers.CharField(max_length=50, required=False)
    sort_by = serializers.CharField(max_length=20, required=False)
    is_featured = serializers.BooleanField(required=False)
    is_new = serializers.BooleanField(required=False)
    is_on_sale = serializers.BooleanField(required=False)


class ProductFilterSerializer(serializers.Serializer):
    """Serializer for product filtering"""
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    price_range = serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2), required=False)
    measurements = serializers.ListField(child=serializers.CharField(), required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    regions = serializers.ListField(child=serializers.CharField(), required=False)
    vintages = serializers.ListField(child=serializers.CharField(), required=False)
    in_stock = serializers.BooleanField(required=False)


class StockUpdateSerializer(serializers.Serializer):
    """Serializer for updating product stock"""
    measurement_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField()
    log_type = serializers.ChoiceField(choices=[
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage'),
    ])
    reference = serializers.CharField(max_length=100, required=False)
    notes = serializers.CharField(max_length=500, required=False)


class ProductStatsSerializer(serializers.Serializer):
    """Serializer for product statistics"""
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    featured_products = serializers.IntegerField()
    new_products = serializers.IntegerField()
    on_sale_products = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    low_stock_products = serializers.IntegerField() 