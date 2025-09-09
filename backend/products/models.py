from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """
    Product categories for organizing products
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def product_count(self):
        return self.products.filter(status='active').count()


class Product(models.Model):
    """
    Product model for alcohol and beverages
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Legacy pricing fields (kept for backward compatibility)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    unit = models.CharField(max_length=20, null=True, blank=True)  # Legacy field
    
    # Inventory (now managed through measurements)
    stock = models.IntegerField(default=0)  # Legacy field - total stock across all measurements
    min_stock_level = models.IntegerField(default=10)
    max_stock_level = models.IntegerField(default=1000)
    
    # Product details
    vintage = models.CharField(max_length=20, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    alcohol_percentage = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    volume = models.CharField(max_length=20, blank=True, null=True)
    
    # Images and media
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    images = models.JSONField(default=list, blank=True)
    
    # Features
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    
    # Ratings and reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    review_count = models.IntegerField(default=0)
    
    # Additional information
    tags = models.JSONField(default=list, blank=True)
    pairings = models.JSONField(default=list, blank=True)
    awards = models.JSONField(default=list, blank=True)
    
    # Bulk pricing
    bulk_pricing = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_available(self):
        return self.status == 'active' and self.stock > 0
    
    @property
    def current_price(self):
        # Get the lowest price from measurements, fallback to legacy price
        from decimal import Decimal
        measurements = self.measurements.filter(is_active=True).order_by('price')
        if measurements.exists():
            return measurements.first().price
        return self.price or Decimal('0')
    
    @property
    def discount_amount(self):
        if self.is_on_sale and self.original_price:
            return self.original_price - self.current_price
        return 0
    
    def update_stock(self, quantity):
        """Update stock level"""
        self.stock = max(0, self.stock + quantity)
        if self.stock == 0:
            self.status = 'out_of_stock'
        elif self.status == 'out_of_stock' and self.stock > 0:
            self.status = 'active'
        self.save()


class ProductMeasurement(models.Model):
    """
    Product measurements with pricing and stock
    """
    MEASUREMENT_CHOICES = [
        ('piece', 'Piece'),
        ('pair', 'Pair'),
        ('dozen', 'Dozen'),
        ('half_dozen', 'Half Dozen'),
        ('box', 'Box'),
        ('carton', 'Carton'),
        ('pack', 'Pack'),
        ('bundle', 'Bundle'),
        ('set', 'Set'),
        ('case', 'Case'),
        ('tray', 'Tray'),
        ('roll', 'Roll'),
        ('bottle', 'Bottle'),
        ('can', 'Can'),
        ('tin', 'Tin'),
        ('barrel', 'Barrel'),
        ('drum', 'Drum'),
        ('sack', 'Sack'),
        ('bag', 'Bag'),
        ('jar', 'Jar'),
        ('tube', 'Tube'),
        ('strip', 'Strip'),
        ('kit', 'Kit'),
        ('shot', 'Shot (30ml or 1oz)'),
        ('nip', 'Nip (50ml)'),
        ('quarter', 'Quarter (180ml)'),
        ('half', 'Half (375ml)'),
        ('pint', 'Pint (473ml / 500ml)'),
        ('fifth', 'Fifth (750ml)'),
        ('liter', 'Liter (1000ml)'),
        ('gallon', 'Gallon (3.78L)'),
        ('keg', 'Keg (varies, e.g., 20L, 30L, 50L)'),
        ('jug', 'Jug'),
        ('flask', 'Flask'),
        ('tumbler', 'Tumbler (glass)'),
        ('mug', 'Mug'),
        ('cup', 'Cup'),
        ('glass', 'Glass'),
        ('crate', 'Crate (collection of bottles or cans)'),
        ('box_wine', 'Box Wine (e.g., 3L, 5L)'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='measurements')
    measurement = models.CharField(max_length=50, choices=MEASUREMENT_CHOICES)
    quantity = models.CharField(max_length=50, null=True, blank=True)  # Custom quantity as string (e.g., "1 unit", "2 pieces")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)  # Default measurement for the product
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_measurements'
        ordering = ['sort_order', 'price']
        unique_together = ['product', 'measurement', 'quantity']
    
    def __str__(self):
        if self.quantity:
            return f"{self.product.name} - {self.quantity} {self.measurement}"
        return f"{self.product.name} - {self.measurement}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default measurement per product
        if self.is_default:
            ProductMeasurement.objects.filter(
                product=self.product, 
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        """Get display name for the measurement"""
        if self.quantity:
            return f"{self.quantity} {self.measurement}"
        return self.get_measurement_display()
    
    @property
    def is_on_sale(self):
        return self.original_price and self.original_price > self.price
    
    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return ((self.original_price - self.price) / self.original_price) * 100
        return 0


class ProductVariant(models.Model):
    """
    Product variants (different sizes, flavors, etc.)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'product_variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductImage(models.Model):
    """
    Additional product images
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class InventoryLog(models.Model):
    """
    Track inventory changes
    """
    LOG_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    measurement = models.ForeignKey(ProductMeasurement, on_delete=models.CASCADE, null=True, blank=True)
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True, null=True)  # Order ID, etc.
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'inventory_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        measurement_info = f" - {self.measurement.display_name}" if self.measurement else ""
        return f"{self.product.name}{measurement_info} - {self.log_type} ({self.quantity})"
