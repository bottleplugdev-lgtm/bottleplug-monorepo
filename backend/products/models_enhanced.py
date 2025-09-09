from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class AlcoholCategory(models.Model):
    """
    Main alcohol categories for Bottleplug
    """
    CATEGORY_TYPES = [
        ('wine', 'Wine'),
        ('spirits', 'Spirits'),
        ('beer', 'Beer & Ciders'),
        ('mixers', 'Mixers & Accessories'),
        ('non_alcoholic', 'Non-Alcoholic'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='alcohol_categories/', null=True, blank=True)
    icon = models.CharField(max_length=10, default='🍷')  # Emoji icon
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    is_age_restricted = models.BooleanField(default=True)  # Most alcohol categories require age verification
    sort_order = models.IntegerField(default=0)
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alcohol_categories'
        verbose_name = 'Alcohol Category'
        verbose_name_plural = 'Alcohol Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def product_count(self):
        return self.alcohol_products.filter(status='active').count()


class Brand(models.Model):
    """
    Alcohol brands and producers
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=200, blank=True, null=True)
    established_year = models.IntegerField(null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    story = models.TextField(blank=True, null=True)  # Brand story and heritage
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'brands'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AlcoholProduct(models.Model):
    """
    Enhanced product model specifically for alcoholic beverages
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre-Order'),
        ('discontinued', 'Discontinued'),
    ]
    
    ALCOHOL_TYPES = [
        # Wines
        ('red_wine', 'Red Wine'),
        ('white_wine', 'White Wine'),
        ('rose_wine', 'Rosé Wine'),
        ('sparkling_wine', 'Sparkling Wine'),
        ('champagne', 'Champagne'),
        ('dessert_wine', 'Dessert Wine'),
        ('fortified_wine', 'Fortified Wine'),
        
        # Spirits
        ('vodka', 'Vodka'),
        ('gin', 'Gin'),
        ('rum', 'Rum'),
        ('whiskey', 'Whiskey'),
        ('bourbon', 'Bourbon'),
        ('scotch', 'Scotch Whisky'),
        ('irish_whiskey', 'Irish Whiskey'),
        ('japanese_whisky', 'Japanese Whisky'),
        ('tequila', 'Tequila'),
        ('mezcal', 'Mezcal'),
        ('cognac', 'Cognac'),
        ('brandy', 'Brandy'),
        ('liqueur', 'Liqueur'),
        
        # Beer & Ciders
        ('ipa', 'IPA'),
        ('lager', 'Lager'),
        ('ale', 'Ale'),
        ('stout', 'Stout'),
        ('porter', 'Porter'),
        ('wheat_beer', 'Wheat Beer'),
        ('sour_beer', 'Sour Beer'),
        ('cider', 'Cider'),
        
        # Non-alcoholic
        ('non_alcoholic', 'Non-Alcoholic'),
    ]
    
    WINE_STYLES = [
        ('dry', 'Dry'),
        ('semi_dry', 'Semi-Dry'),
        ('semi_sweet', 'Semi-Sweet'),
        ('sweet', 'Sweet'),
        ('brut', 'Brut'),
        ('extra_brut', 'Extra Brut'),
        ('demi_sec', 'Demi-Sec'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(AlcoholCategory, on_delete=models.CASCADE, related_name='alcohol_products')
    alcohol_type = models.CharField(max_length=50, choices=ALCOHOL_TYPES)
    description = models.TextField(blank=True, null=True)
    short_description = models.CharField(max_length=500, blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Alcohol-Specific Details
    alcohol_percentage = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    volume_ml = models.IntegerField(null=True, blank=True)  # Volume in milliliters
    vintage = models.CharField(max_length=10, blank=True, null=True)
    wine_style = models.CharField(max_length=20, choices=WINE_STYLES, blank=True, null=True)
    
    # Origin Information
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=200, blank=True, null=True)
    appellation = models.CharField(max_length=200, blank=True, null=True)  # For wines
    vineyard = models.CharField(max_length=200, blank=True, null=True)
    distillery = models.CharField(max_length=200, blank=True, null=True)  # For spirits
    
    # Tasting Information
    tasting_notes = models.TextField(blank=True, null=True)
    aroma_profile = models.JSONField(default=list, blank=True)  # ['citrus', 'vanilla', 'oak']
    flavor_profile = models.JSONField(default=list, blank=True)  # ['fruity', 'spicy', 'smooth']
    finish = models.CharField(max_length=200, blank=True, null=True)  # 'Long and smooth'
    body = models.CharField(max_length=50, blank=True, null=True)  # 'Full-bodied', 'Light', 'Medium'
    
    # Food Pairing
    food_pairings = models.JSONField(default=list, blank=True)  # ['beef', 'dark chocolate', 'aged cheese']
    serving_temperature = models.CharField(max_length=50, blank=True, null=True)  # '16-18°C'
    decanting_time = models.CharField(max_length=50, blank=True, null=True)  # '30 minutes'
    glassware = models.CharField(max_length=100, blank=True, null=True)  # 'Bordeaux glass'
    
    # Awards and Ratings
    awards = models.JSONField(default=list, blank=True)
    wine_spectator_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    robert_parker_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    james_suckling_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    decanter_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Pricing
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    msrp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Manufacturer suggested retail price
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # For margin calculation
    
    # Inventory
    stock_quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)  # Reserved for pending orders
    min_stock_level = models.IntegerField(default=5)
    max_stock_level = models.IntegerField(default=1000)
    reorder_point = models.IntegerField(default=10)
    
    # Product Features
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    is_limited_edition = models.BooleanField(default=False)
    is_organic = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    contains_sulfites = models.BooleanField(default=True)
    
    # Age Restrictions
    age_restriction = models.IntegerField(default=21)  # Minimum age required
    requires_id_verification = models.BooleanField(default=True)
    
    # SEO and Marketing
    tags = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    
    # Images
    primary_image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # Customer Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_reviews = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alcohol_products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'alcohol_type']),
            models.Index(fields=['brand', 'vintage']),
            models.Index(fields=['base_price']),
            models.Index(fields=['average_rating']),
        ]
    
    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.vintage if self.vintage else 'NV'})"
    
    @property
    def available_quantity(self):
        return self.stock_quantity - self.reserved_quantity
    
    @property
    def is_available(self):
        return self.status == 'active' and self.available_quantity > 0
    
    @property
    def is_low_stock(self):
        return self.available_quantity <= self.min_stock_level
    
    @property
    def current_price(self):
        # Get the best price from size variants
        sizes = self.size_variants.filter(is_active=True).order_by('price')
        if sizes.exists():
            return sizes.first().price
        return self.base_price
    
    @property
    def display_name(self):
        vintage_part = f" {self.vintage}" if self.vintage else ""
        return f"{self.brand.name} {self.name}{vintage_part}"
    
    @property
    def expert_score_average(self):
        scores = [
            self.wine_spectator_score,
            self.robert_parker_score, 
            self.james_suckling_score,
            self.decanter_score
        ]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else None


class ProductSizeVariant(models.Model):
    """
    Different size variants for alcohol products (e.g., 750ml, 1.5L, etc.)
    """
    SIZE_CHOICES = [
        # Wine sizes
        ('187ml', '187ml (Split)'),
        ('375ml', '375ml (Half Bottle)'),
        ('750ml', '750ml (Standard)'),
        ('1000ml', '1L (Liter)'),
        ('1500ml', '1.5L (Magnum)'),
        ('3000ml', '3L (Double Magnum)'),
        ('4500ml', '4.5L (Jeroboam)'),
        ('6000ml', '6L (Imperial)'),
        ('9000ml', '9L (Salmanazar)'),
        
        # Spirit sizes
        ('50ml', '50ml (Miniature)'),
        ('100ml', '100ml'),
        ('200ml', '200ml (Half Pint)'),
        ('350ml', '350ml'),
        ('700ml', '700ml'),
        ('1750ml', '1.75L (Half Gallon)'),
        
        # Beer sizes
        ('330ml', '330ml (Bottle)'),
        ('355ml', '355ml (Can)'),
        ('500ml', '500ml (Pint)'),
        ('650ml', '650ml (Bomber)'),
        ('22oz', '22oz'),
        
        # Bulk sizes
        ('case_6', 'Case of 6'),
        ('case_12', 'Case of 12'),
        ('case_24', 'Case of 24'),
    ]
    
    product = models.ForeignKey(AlcoholProduct, on_delete=models.CASCADE, related_name='size_variants')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    volume_ml = models.IntegerField()  # Actual volume in ml
    price = models.DecimalField(max_digits=12, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    weight_grams = models.IntegerField(null=True, blank=True)  # For shipping calculations
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_size_variants'
        unique_together = ['product', 'size']
        ordering = ['sort_order', 'volume_ml']
    
    def __str__(self):
        return f"{self.product.display_name} - {self.get_size_display()}"
    
    @property
    def price_per_ml(self):
        return self.price / self.volume_ml if self.volume_ml > 0 else 0


class ProductImage(models.Model):
    """
    Multiple images for products
    """
    product = models.ForeignKey(AlcoholProduct, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    image_type = models.CharField(max_length=50, choices=[
        ('main', 'Main Product'),
        ('label', 'Label Close-up'),
        ('bottle', 'Bottle Shape'),
        ('lifestyle', 'Lifestyle'),
        ('packaging', 'Packaging'),
    ], default='main')
    
    class Meta:
        db_table = 'product_images'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"{self.product.display_name} - {self.image_type}"


class TasteProfile(models.Model):
    """
    Customer taste profiles for personalized recommendations
    """
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='taste_profile')
    
    # Wine preferences
    preferred_wine_styles = models.JSONField(default=list, blank=True)  # ['dry', 'full-bodied']
    preferred_wine_regions = models.JSONField(default=list, blank=True)  # ['bordeaux', 'napa']
    preferred_grape_varieties = models.JSONField(default=list, blank=True)  # ['cabernet', 'chardonnay']
    
    # Spirit preferences
    preferred_spirit_types = models.JSONField(default=list, blank=True)  # ['whiskey', 'gin']
    preferred_spirit_characteristics = models.JSONField(default=list, blank=True)  # ['smooth', 'smoky']
    
    # Flavor preferences
    preferred_flavors = models.JSONField(default=list, blank=True)  # ['fruity', 'spicy', 'vanilla']
    disliked_flavors = models.JSONField(default=list, blank=True)  # ['too_sweet', 'bitter']
    
    # Price preferences
    typical_price_range_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    typical_price_range_max = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    
    # Occasions
    preferred_occasions = models.JSONField(default=list, blank=True)  # ['dinner', 'celebration', 'casual']
    
    # Learning data
    purchase_history_analyzed = models.BooleanField(default=False)
    last_analysis_date = models.DateTimeField(null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0-100
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'taste_profiles'
    
    def __str__(self):
        return f"Taste Profile for {self.user.email}"


class ProductRecommendation(models.Model):
    """
    AI-generated product recommendations
    """
    RECOMMENDATION_TYPES = [
        ('similar', 'Similar Products'),
        ('frequently_bought', 'Frequently Bought Together'),
        ('user_based', 'Users Like You Also Bought'),
        ('trending', 'Trending Now'),
        ('seasonal', 'Seasonal Picks'),
        ('occasion', 'Perfect For This Occasion'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='recommendations', null=True, blank=True)
    product = models.ForeignKey(AlcoholProduct, on_delete=models.CASCADE, related_name='recommendations')
    recommended_products = models.ManyToManyField(AlcoholProduct, related_name='recommended_for', through='RecommendationScore')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)  # 0-100
    reason = models.TextField(blank=True, null=True)  # Why this recommendation was made
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'product_recommendations'
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['product', 'confidence_score']),
        ]


class RecommendationScore(models.Model):
    """
    Through model for recommendation scores
    """
    recommendation = models.ForeignKey(ProductRecommendation, on_delete=models.CASCADE)
    recommended_product = models.ForeignKey(AlcoholProduct, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    rank = models.IntegerField()
    
    class Meta:
        db_table = 'recommendation_scores'
        ordering = ['rank']


class ProductReview(models.Model):
    """
    Customer product reviews and ratings
    """
    product = models.ForeignKey(AlcoholProduct, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='product_reviews')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)  # Verified purchase
    
    # Ratings
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    taste_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    value_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    packaging_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    # Review content
    title = models.CharField(max_length=200, blank=True, null=True)
    review_text = models.TextField(blank=True, null=True)
    
    # Tasting notes from customer
    customer_tasting_notes = models.TextField(blank=True, null=True)
    occasion = models.CharField(max_length=100, blank=True, null=True)  # When they enjoyed it
    food_paired_with = models.CharField(max_length=200, blank=True, null=True)
    
    # Review metadata
    is_verified_purchase = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_reviews'
        unique_together = ['product', 'user', 'order']  # One review per product per order
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review of {self.product.display_name} by {self.user.email}"


class Collection(models.Model):
    """
    Curated product collections (e.g., "Summer Wines", "Whiskey Essentials")
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=300, unique=True)
    image = models.ImageField(upload_to='collections/', null=True, blank=True)
    products = models.ManyToManyField(AlcoholProduct, related_name='collections', through='CollectionProduct')
    
    # Collection type
    collection_type = models.CharField(max_length=50, choices=[
        ('curated', 'Curated by Experts'),
        ('seasonal', 'Seasonal'),
        ('occasion', 'Occasion-Based'),
        ('region', 'Regional'),
        ('price', 'Price-Based'),
        ('trending', 'Trending'),
    ], default='curated')
    
    # Display settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collections'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class CollectionProduct(models.Model):
    """
    Through model for collection products with additional metadata
    """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    product = models.ForeignKey(AlcoholProduct, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)  # Highlight within collection
    curator_notes = models.TextField(blank=True, null=True)  # Why this product is in the collection
    
    class Meta:
        db_table = 'collection_products'
        unique_together = ['collection', 'product']
        ordering = ['sort_order']


class InventoryMovement(models.Model):
    """
    Track all inventory movements for audit purposes
    """
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase/Receiving'),
        ('sale', 'Sale'),
        ('adjustment', 'Stock Adjustment'),
        ('damage', 'Damage/Loss'),
        ('return', 'Customer Return'),
        ('transfer', 'Transfer Between Locations'),
        ('reservation', 'Stock Reservation'),
        ('release', 'Reservation Release'),
    ]
    
    product = models.ForeignKey(AlcoholProduct, on_delete=models.CASCADE, related_name='inventory_movements')
    size_variant = models.ForeignKey(ProductSizeVariant, on_delete=models.CASCADE, null=True, blank=True)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Positive for incoming, negative for outgoing
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_number = models.CharField(max_length=100, blank=True, null=True)  # Order ID, PO number, etc.
    notes = models.TextField(blank=True, null=True)
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Tracking
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'inventory_movements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'movement_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.product.display_name} - {self.movement_type} ({self.quantity})"
