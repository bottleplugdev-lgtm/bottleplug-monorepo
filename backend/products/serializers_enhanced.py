from rest_framework import serializers
from decimal import Decimal
from .models_enhanced import (
    AlcoholCategory, Brand, AlcoholProduct, ProductSizeVariant, 
    ProductImage, TasteProfile, ProductRecommendation, ProductReview, 
    Collection, InventoryMovement
)


class AlcoholCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for alcohol categories with subcategory nesting
    """
    subcategories = serializers.SerializerMethodField()
    product_count = serializers.ReadOnlyField()
    
    class Meta:
        model = AlcoholCategory
        fields = [
            'id', 'name', 'category_type', 'description', 'image', 'icon', 
            'parent', 'subcategories', 'is_active', 'is_age_restricted', 
            'sort_order', 'product_count', 'seo_title', 'seo_description',
            'created_at', 'updated_at'
        ]
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return AlcoholCategorySerializer(obj.subcategories.all(), many=True).data
        return []


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for alcohol brands
    """
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'description', 'logo', 'country', 'region',
            'established_year', 'website', 'story', 'is_active', 'is_featured',
            'product_count', 'created_at', 'updated_at'
        ]
    
    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductSizeVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for product size variants
    """
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    price_per_ml = serializers.ReadOnlyField()
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductSizeVariant
        fields = [
            'id', 'size', 'size_display', 'volume_ml', 'price', 'wholesale_price',
            'stock_quantity', 'sku', 'is_default', 'is_active', 'weight_grams',
            'price_per_ml', 'is_in_stock', 'sort_order'
        ]
    
    def get_is_in_stock(self, obj):
        return obj.stock_quantity > 0


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product images
    """
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'is_primary', 'sort_order', 'image_type'
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for product reviews
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'overall_rating', 'taste_rating', 'value_rating', 'packaging_rating',
            'title', 'review_text', 'customer_tasting_notes', 'occasion', 
            'food_paired_with', 'is_verified_purchase', 'is_featured', 
            'helpful_votes', 'user_name', 'user_avatar', 'created_at'
        ]
    
    def get_user_avatar(self, obj):
        if hasattr(obj.user, 'profile_image') and obj.user.profile_image:
            return obj.user.profile_image.url
        return None


class AlcoholProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product lists and search results
    """
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    alcohol_type_display = serializers.CharField(source='get_alcohol_type_display', read_only=True)
    wine_style_display = serializers.CharField(source='get_wine_style_display', read_only=True)
    display_name = serializers.ReadOnlyField()
    current_price = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    expert_score_average = serializers.ReadOnlyField()
    size_options = serializers.SerializerMethodField()
    primary_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AlcoholProduct
        fields = [
            'id', 'name', 'display_name', 'brand_name', 'category_name', 
            'alcohol_type', 'alcohol_type_display', 'wine_style', 'wine_style_display',
            'short_description', 'vintage', 'country', 'region', 'alcohol_percentage',
            'base_price', 'current_price', 'stock_quantity', 'is_available',
            'is_featured', 'is_new_arrival', 'is_on_sale', 'is_limited_edition',
            'is_organic', 'is_vegan', 'is_gluten_free', 'average_rating', 
            'total_reviews', 'expert_score_average', 'size_options',
            'primary_image', 'primary_image_url', 'tags', 'slug'
        ]
    
    def get_size_options(self, obj):
        sizes = obj.size_variants.filter(is_active=True).order_by('sort_order', 'volume_ml')
        return ProductSizeVariantSerializer(sizes, many=True).data
    
    def get_primary_image_url(self, obj):
        if obj.primary_image:
            return obj.primary_image.url
        # Fallback to first image
        primary_img = obj.images.filter(is_primary=True).first()
        if primary_img:
            return primary_img.image.url
        return None


class AlcoholProductDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for product detail pages
    """
    brand = BrandSerializer(read_only=True)
    category = AlcoholCategorySerializer(read_only=True)
    size_variants = ProductSizeVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    
    # Computed fields
    alcohol_type_display = serializers.CharField(source='get_alcohol_type_display', read_only=True)
    wine_style_display = serializers.CharField(source='get_wine_style_display', read_only=True)
    display_name = serializers.ReadOnlyField()
    current_price = serializers.ReadOnlyField()
    available_quantity = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    expert_score_average = serializers.ReadOnlyField()
    
    # Related data
    similar_products = serializers.SerializerMethodField()
    frequently_bought_together = serializers.SerializerMethodField()
    
    class Meta:
        model = AlcoholProduct
        exclude = ['created_at', 'updated_at']  # Include all fields except timestamps
    
    def get_reviews(self, obj):
        # Get recent reviews (limit to 10 for performance)
        recent_reviews = obj.reviews.order_by('-created_at')[:10]
        return ProductReviewSerializer(recent_reviews, many=True).data
    
    def get_similar_products(self, obj):
        # Find similar products by category and alcohol type
        similar = AlcoholProduct.objects.filter(
            category=obj.category,
            alcohol_type=obj.alcohol_type,
            status='active'
        ).exclude(id=obj.id)[:6]
        return AlcoholProductListSerializer(similar, many=True).data
    
    def get_frequently_bought_together(self, obj):
        # This would be implemented with actual purchase data analysis
        # For now, return empty list
        return []


class AlcoholProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating alcohol products
    """
    class Meta:
        model = AlcoholProduct
        fields = [
            'name', 'brand', 'category', 'alcohol_type', 'description', 
            'short_description', 'sku', 'barcode', 'status', 'alcohol_percentage',
            'volume_ml', 'vintage', 'wine_style', 'country', 'region', 
            'appellation', 'vineyard', 'distillery', 'tasting_notes',
            'aroma_profile', 'flavor_profile', 'finish', 'body', 'food_pairings',
            'serving_temperature', 'decanting_time', 'glassware', 'awards',
            'wine_spectator_score', 'robert_parker_score', 'james_suckling_score',
            'decanter_score', 'base_price', 'wholesale_price', 'msrp', 'cost_price',
            'stock_quantity', 'min_stock_level', 'max_stock_level', 'reorder_point',
            'is_featured', 'is_new_arrival', 'is_on_sale', 'is_limited_edition',
            'is_organic', 'is_vegan', 'is_gluten_free', 'contains_sulfites',
            'age_restriction', 'requires_id_verification', 'tags', 'meta_title',
            'meta_description', 'slug', 'primary_image'
        ]
    
    def validate_sku(self, value):
        instance = getattr(self, 'instance', None)
        if AlcoholProduct.objects.exclude(id=instance.id if instance else None).filter(sku=value).exists():
            raise serializers.ValidationError("Product with this SKU already exists.")
        return value
    
    def validate_base_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate_alcohol_percentage(self, value):
        if value and (value < 0 or value > 100):
            raise serializers.ValidationError("Alcohol percentage must be between 0 and 100.")
        return value


class TasteProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user taste profiles
    """
    class Meta:
        model = TasteProfile
        fields = [
            'preferred_wine_styles', 'preferred_wine_regions', 'preferred_grape_varieties',
            'preferred_spirit_types', 'preferred_spirit_characteristics',
            'preferred_flavors', 'disliked_flavors', 'typical_price_range_min',
            'typical_price_range_max', 'preferred_occasions', 'confidence_score',
            'last_analysis_date'
        ]


class ProductRecommendationSerializer(serializers.ModelSerializer):
    """
    Serializer for product recommendations
    """
    recommended_products = AlcoholProductListSerializer(many=True, read_only=True)
    recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
    
    class Meta:
        model = ProductRecommendation
        fields = [
            'id', 'recommendation_type', 'recommendation_type_display',
            'recommended_products', 'confidence_score', 'reason', 'created_at'
        ]


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for product collections
    """
    products = AlcoholProductListSerializer(many=True, read_only=True)
    product_count = serializers.SerializerMethodField()
    collection_type_display = serializers.CharField(source='get_collection_type_display', read_only=True)
    
    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'description', 'slug', 'image', 'collection_type',
            'collection_type_display', 'products', 'product_count', 'is_active',
            'is_featured', 'meta_title', 'meta_description'
        ]
    
    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductSearchSerializer(serializers.Serializer):
    """
    Serializer for advanced product search
    """
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    alcohol_type = serializers.ChoiceField(
        choices=AlcoholProduct.ALCOHOL_TYPES, 
        required=False, 
        allow_blank=True
    )
    brand = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    vintage = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    min_alcohol_percentage = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    max_alcohol_percentage = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    min_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    
    # Filters
    is_featured = serializers.BooleanField(required=False)
    is_new_arrival = serializers.BooleanField(required=False)
    is_on_sale = serializers.BooleanField(required=False)
    is_organic = serializers.BooleanField(required=False)
    is_vegan = serializers.BooleanField(required=False)
    is_gluten_free = serializers.BooleanField(required=False)
    in_stock = serializers.BooleanField(required=False)
    
    # Sorting
    sort_by = serializers.ChoiceField(
        choices=[
            ('name', 'Name'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating', 'Customer Rating'),
            ('expert_score', 'Expert Score'),
            ('newest', 'Newest First'),
            ('popularity', 'Most Popular'),
            ('vintage', 'Vintage Year'),
        ],
        default='newest',
        required=False
    )


class ProductFilterSerializer(serializers.Serializer):
    """
    Serializer for product filtering options
    """
    categories = AlcoholCategorySerializer(many=True, read_only=True)
    brands = BrandSerializer(many=True, read_only=True)
    alcohol_types = serializers.SerializerMethodField()
    countries = serializers.SerializerMethodField()
    regions = serializers.SerializerMethodField()
    vintages = serializers.SerializerMethodField()
    price_ranges = serializers.SerializerMethodField()
    
    def get_alcohol_types(self):
        return [{'value': choice[0], 'label': choice[1]} for choice in AlcoholProduct.ALCOHOL_TYPES]
    
    def get_countries(self):
        # Get unique countries from active products
        countries = AlcoholProduct.objects.filter(
            status='active', 
            country__isnull=False
        ).values_list('country', flat=True).distinct().order_by('country')
        return list(countries)
    
    def get_regions(self):
        # Get unique regions from active products
        regions = AlcoholProduct.objects.filter(
            status='active',
            region__isnull=False
        ).values_list('region', flat=True).distinct().order_by('region')
        return list(regions)
    
    def get_vintages(self):
        # Get unique vintages from active products
        vintages = AlcoholProduct.objects.filter(
            status='active',
            vintage__isnull=False
        ).values_list('vintage', flat=True).distinct().order_by('-vintage')
        return list(vintages)
    
    def get_price_ranges(self):
        return [
            {'label': 'Under $25', 'min': 0, 'max': 25},
            {'label': '$25 - $50', 'min': 25, 'max': 50},
            {'label': '$50 - $100', 'min': 50, 'max': 100},
            {'label': '$100 - $250', 'min': 100, 'max': 250},
            {'label': '$250 - $500', 'min': 250, 'max': 500},
            {'label': '$500+', 'min': 500, 'max': 10000},
        ]


class InventoryMovementSerializer(serializers.ModelSerializer):
    """
    Serializer for inventory movements
    """
    product_name = serializers.CharField(source='product.display_name', read_only=True)
    size_variant_display = serializers.CharField(source='size_variant.__str__', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'product_name', 'size_variant_display', 'movement_type',
            'movement_type_display', 'quantity', 'previous_stock', 'new_stock',
            'reference_number', 'notes', 'cost_per_unit', 'total_value',
            'created_by_name', 'created_at'
        ]


class ProductStatsSerializer(serializers.Serializer):
    """
    Serializer for product statistics
    """
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    featured_products = serializers.IntegerField()
    new_arrival_products = serializers.IntegerField()
    on_sale_products = serializers.IntegerField()
    total_brands = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    total_reviews = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating product reviews
    """
    class Meta:
        model = ProductReview
        fields = [
            'product', 'overall_rating', 'taste_rating', 'value_rating',
            'packaging_rating', 'title', 'review_text', 'customer_tasting_notes',
            'occasion', 'food_paired_with'
        ]
    
    def validate_overall_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        # Set user and check for verified purchase
        validated_data['user'] = self.context['request'].user
        
        # Check if this is a verified purchase
        product = validated_data['product']
        user = validated_data['user']
        
        # Check if user has purchased this product
        from orders.models import Order, OrderItem
        verified_order = Order.objects.filter(
            user=user,
            order_items__product_id=product.id,
            status='delivered'
        ).first()
        
        if verified_order:
            validated_data['order'] = verified_order
            validated_data['is_verified_purchase'] = True
        
        return super().create(validated_data)
