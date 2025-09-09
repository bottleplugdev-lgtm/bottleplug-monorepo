from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class AnalyticsEvent(models.Model):
    """
    Track various analytics events
    """
    EVENT_TYPE_CHOICES = [
        # User events
        ('user_signup', 'User Signup'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('profile_update', 'Profile Update'),
        
        # Product events
        ('product_view', 'Product View'),
        ('product_search', 'Product Search'),
        ('product_add_to_cart', 'Product Added to Cart'),
        ('product_remove_from_cart', 'Product Removed from Cart'),
        ('product_purchase', 'Product Purchase'),
        ('product_review', 'Product Review'),
        
        # Order events
        ('order_created', 'Order Created'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_cancelled', 'Order Cancelled'),
        ('order_delivered', 'Order Delivered'),
        ('payment_success', 'Payment Success'),
        ('payment_failed', 'Payment Failed'),
        
        # Delivery events
        ('delivery_requested', 'Delivery Requested'),
        ('delivery_accepted', 'Delivery Accepted'),
        ('delivery_picked_up', 'Delivery Picked Up'),
        ('delivery_delivered', 'Delivery Delivered'),
        ('delivery_cancelled', 'Delivery Cancelled'),
        
        # App events
        ('app_open', 'App Open'),
        ('app_close', 'App Close'),
        ('page_view', 'Page View'),
        ('button_click', 'Button Click'),
    ]
    
    # Event information
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    
    # Generic foreign key for related objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Event data
    event_data = models.JSONField(default=dict, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Device and location
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'analytics_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.user.email if self.user else 'Anonymous'} - {self.created_at}"


class UserMetrics(models.Model):
    """
    Daily user metrics
    """
    date = models.DateField(unique=True)
    
    # User counts
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    returning_users = models.IntegerField(default=0)
    
    # User types
    customers = models.IntegerField(default=0)
    drivers = models.IntegerField(default=0)
    admins = models.IntegerField(default=0)
    
    # Engagement
    total_sessions = models.IntegerField(default=0)
    avg_session_duration = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # in minutes
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_metrics'
        ordering = ['-date']
    
    def __str__(self):
        return f"User Metrics - {self.date}"


class ProductMetrics(models.Model):
    """
    Daily product metrics
    """
    date = models.DateField()
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='metrics')
    
    # Views and engagement
    views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    add_to_cart_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    
    # Revenue
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Ratings
    new_reviews = models.IntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_metrics'
        unique_together = ['date', 'product']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.product.name} - {self.date}"


class OrderMetrics(models.Model):
    """
    Daily order metrics
    """
    date = models.DateField(unique=True)
    
    # Order counts
    total_orders = models.IntegerField(default=0)
    new_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    
    # Revenue
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment methods
    cash_payments = models.IntegerField(default=0)
    card_payments = models.IntegerField(default=0)
    mobile_money_payments = models.IntegerField(default=0)
    wallet_payments = models.IntegerField(default=0)
    
    # Conversion
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_metrics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Order Metrics - {self.date}"


class DeliveryMetrics(models.Model):
    """
    Daily delivery metrics
    """
    date = models.DateField(unique=True)
    
    # Delivery counts
    total_deliveries = models.IntegerField(default=0)
    new_deliveries = models.IntegerField(default=0)
    completed_deliveries = models.IntegerField(default=0)
    cancelled_deliveries = models.IntegerField(default=0)
    
    # Performance
    avg_delivery_time = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # in minutes
    avg_delivery_distance = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # in km
    
    # Revenue
    total_delivery_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Driver metrics
    active_drivers = models.IntegerField(default=0)
    avg_driver_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'delivery_metrics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Delivery Metrics - {self.date}"


class RevenueMetrics(models.Model):
    """
    Revenue tracking by period
    """
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Revenue breakdown
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    product_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Costs and profit
    total_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    
    # Growth
    revenue_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    order_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'revenue_metrics'
        unique_together = ['period_type', 'period_start', 'period_end']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"Revenue {self.period_type} - {self.period_start} to {self.period_end}"


class SearchAnalytics(models.Model):
    """
    Track search queries and results
    """
    query = models.CharField(max_length=500)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    
    # Results
    results_count = models.IntegerField(default=0)
    clicked_results = models.JSONField(default=list, blank=True)  # List of clicked product IDs
    
    # Performance
    search_time = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)  # in seconds
    is_successful = models.BooleanField(default=True)  # Did user find what they were looking for?
    
    # Context
    category_filter = models.CharField(max_length=100, blank=True, null=True)
    price_filter = models.CharField(max_length=50, blank=True, null=True)
    sort_by = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'search_analytics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Search: {self.query[:50]}... - {self.created_at}"
