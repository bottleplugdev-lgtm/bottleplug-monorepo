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


class InventoryItem(models.Model):
    """
    Real-time inventory tracking for products
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')

    # Stock levels
    current_stock = models.IntegerField(default=0)
    reserved_stock = models.IntegerField(default=0)  # Reserved for pending orders
    available_stock = models.IntegerField(default=0)  # current_stock - reserved_stock

    # Stock management
    min_stock_level = models.IntegerField(default=10)
    max_stock_level = models.IntegerField(default=1000)
    reorder_point = models.IntegerField(default=20)
    reorder_quantity = models.IntegerField(default=100)

    # Settings
    is_active = models.BooleanField(default=True)
    allow_backorders = models.BooleanField(default=False)
    track_quantity = models.BooleanField(default=True)

    # Location and supplier info
    location = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.CharField(max_length=200, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Batch tracking
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    last_stock_check = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_items'
        indexes = [
            models.Index(fields=['current_stock', 'min_stock_level']),
            models.Index(fields=['available_stock']),
            models.Index(fields=['last_updated']),
        ]

    def __str__(self):
        return f"Inventory: {self.product.name} (Available: {self.available_stock})"

    @property
    def is_in_stock(self):
        """Check if item is in stock"""
        return self.available_stock > 0

    @property
    def is_out_of_stock(self):
        """Check if item is out of stock"""
        return self.available_stock <= 0

    @property
    def is_low_stock(self):
        """Check if item is low stock"""
        return self.available_stock <= self.min_stock_level and self.min_stock_level > 0

    @property
    def needs_reorder(self):
        """Check if item needs reordering"""
        return self.available_stock <= self.reorder_point and self.reorder_point > 0

    @property
    def is_overstocked(self):
        """Check if item is overstocked"""
        return self.current_stock > self.max_stock_level and self.max_stock_level > 0

    @property
    def stock_status(self):
        """Get stock status"""
        if self.is_out_of_stock:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        elif self.is_overstocked:
            return 'overstock'
        return 'in_stock'

    @property
    def stock_level_percentage(self):
        """Get stock level percentage"""
        if self.max_stock_level <= 0:
            return 0.0
        return min((self.current_stock / self.max_stock_level) * 100, 100.0)

    @property
    def days_until_expiry(self):
        """Get days until expiry"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now()).days

    @property
    def is_expired(self):
        """Check if item is expired"""
        if not self.expiry_date:
            return False
        return timezone.now() > self.expiry_date

    @property
    def is_expiring_soon(self):
        """Check if item is expiring soon (within 30 days)"""
        days = self.days_until_expiry
        return days is not None and 0 < days <= 30

    def can_reserve(self, quantity):
        """Check if quantity can be reserved"""
        return (self.available_stock - quantity) >= 0

    def reserve_stock(self, quantity, reference=None):
        """Reserve stock for an order"""
        if not self.can_reserve(quantity):
            return False

        self.reserved_stock += quantity
        self.available_stock = self.current_stock - self.reserved_stock
        self.save()

        # Create stock movement record
        StockMovement.objects.create(
            inventory_item=self,
            movement_type='reservation',
            quantity=-quantity,
            previous_stock=self.available_stock + quantity,
            new_stock=self.available_stock,
            reference=reference,
            notes=f"Reserved {quantity} units"
        )

        return True

    def release_stock(self, quantity, reference=None):
        """Release reserved stock"""
        release_qty = min(quantity, self.reserved_stock)
        self.reserved_stock -= release_qty
        self.available_stock = self.current_stock - self.reserved_stock
        self.save()

        # Create stock movement record
        StockMovement.objects.create(
            inventory_item=self,
            movement_type='release',
            quantity=release_qty,
            previous_stock=self.available_stock - release_qty,
            new_stock=self.available_stock,
            reference=reference,
            notes=f"Released {release_qty} units"
        )

        return release_qty

    def update_stock(self, new_stock, movement_type='adjustment', reference=None, notes=None):
        """Update stock level and create movement record"""
        previous_stock = self.current_stock
        quantity_change = new_stock - previous_stock

        self.current_stock = max(0, new_stock)
        self.available_stock = self.current_stock - self.reserved_stock
        self.save()

        # Create stock movement record
        StockMovement.objects.create(
            inventory_item=self,
            movement_type=movement_type,
            quantity=quantity_change,
            previous_stock=previous_stock,
            new_stock=self.current_stock,
            reference=reference,
            notes=notes or f"Stock updated from {previous_stock} to {self.current_stock}"
        )

        # Update product stock (legacy field)
        self.product.stock = self.current_stock
        if self.current_stock == 0:
            self.product.status = 'out_of_stock'
        elif self.product.status == 'out_of_stock' and self.current_stock > 0:
            self.product.status = 'active'
        self.product.save()

        # Check for notifications
        self._check_stock_alerts()

        return quantity_change

    def _check_stock_alerts(self):
        """Check and send stock alerts"""
        from notifications.services import NotificationService

        # Check for low stock alerts
        if self.is_low_stock and self.track_quantity:
            # Notify admin users about low stock
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_users = User.objects.filter(is_staff=True)

            for admin in admin_users:
                NotificationService.notify_user(
                    admin.id,
                    f"Low Stock Alert: {self.product.name}",
                    f"Stock level is {self.available_stock}, below minimum of {self.min_stock_level}",
                    'stock_alert',
                    {
                        'product_id': self.product.id,
                        'current_stock': self.available_stock,
                        'min_stock': self.min_stock_level,
                        'alert_type': 'low_stock'
                    }
                )

        # Check for restock notifications (when item comes back in stock)
        if self.is_in_stock and hasattr(self, '_was_out_of_stock') and self._was_out_of_stock:
            # Notify users with wishlist items
            wishlist_items = self.product.wishlist_set.filter(stock_alerts=True)
            for wishlist_item in wishlist_items:
                NotificationService.notify_user(
                    wishlist_item.user.id,
                    f"{self.product.name} is back in stock!",
                    f"Your wishlist item is now available with {self.available_stock} units in stock.",
                    'stock_alert',
                    {
                        'product_id': self.product.id,
                        'wishlist_id': wishlist_item.id,
                        'available_stock': self.available_stock,
                        'alert_type': 'back_in_stock'
                    }
                )
                wishlist_item.update_stock_tracking()

            # Notify pre-order customers
            pre_orders = self.product.pre_orders.filter(status='pending', notify_when_available=True)
            for pre_order in pre_orders:
                if pre_order.can_be_fulfilled:
                    pre_order.send_availability_notification()

    def save(self, *args, **kwargs):
        # Track if item was out of stock before save
        if self.pk:
            old_item = InventoryItem.objects.get(pk=self.pk)
            self._was_out_of_stock = old_item.is_out_of_stock

        # Calculate available stock
        self.available_stock = self.current_stock - self.reserved_stock
        super().save(*args, **kwargs)


class StockMovement(models.Model):
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
        ('restock', 'Restock'),
        ('expired', 'Expired Stock Removal'),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Positive for incoming, negative for outgoing
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()

    # Reference information
    reference = models.CharField(max_length=100, blank=True, null=True)  # Order ID, PO number, etc.
    notes = models.TextField(blank=True, null=True)

    # Cost tracking
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Tracking
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'stock_movements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_item', 'movement_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['reference']),
        ]

    def __str__(self):
        return f"{self.inventory_item.product.name} - {self.movement_type} ({self.quantity})"

    @property
    def is_incoming(self):
        """Check if this is an incoming movement"""
        return self.quantity > 0

    @property
    def is_outgoing(self):
        """Check if this is an outgoing movement"""
        return self.quantity < 0

    def save(self, *args, **kwargs):
        # Calculate total value if cost per unit is provided
        if self.cost_per_unit and not self.total_value:
            self.total_value = abs(self.quantity) * self.cost_per_unit
        super().save(*args, **kwargs)


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
