from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class DeliveryRequest(models.Model):
    """
    Delivery requests from customers
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Request information
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='delivery_requests')
    driver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deliveries')
    
    # Addresses
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    tracking_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, default='cash')
    
    # Timing
    estimated_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in minutes
    actual_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in minutes
    distance = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # in kilometers
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    cancel_reason = models.TextField(blank=True, null=True)
    items = models.JSONField(default=dict, blank=True)  # Package contents
    customer_signature = models.TextField(blank=True, null=True)
    driver_signature = models.TextField(blank=True, null=True)
    images = models.JSONField(default=list, blank=True)  # Delivery proof images
    
    class Meta:
        db_table = 'delivery_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery {self.tracking_code} - {self.customer.email}"
    
    def save(self, *args, **kwargs):
        # Generate tracking code if not provided
        if not self.tracking_code:
            self.tracking_code = self._generate_tracking_code()
        
        super().save(*args, **kwargs)
    
    def _generate_tracking_code(self):
        """Generate unique tracking code"""
        import random
        import string
        
        while True:
            # Format: DEL-XXXXXX
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            tracking_code = f"DEL-{random_part}"
            
            if not DeliveryRequest.objects.filter(tracking_code=tracking_code).exists():
                return tracking_code
    
    @property
    def total_amount(self):
        return self.amount + self.delivery_fee
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_accepted(self):
        return self.status == 'accepted'
    
    @property
    def is_picked_up(self):
        return self.status == 'picked_up'
    
    @property
    def is_in_transit(self):
        return self.status == 'in_transit'
    
    @property
    def is_delivered(self):
        return self.status == 'delivered'
    
    @property
    def is_cancelled(self):
        return self.status == 'cancelled'
    
    @property
    def is_active(self):
        return not self.is_delivered and not self.is_cancelled
    
    @property
    def is_completed(self):
        return self.is_delivered


class DriverLocation(models.Model):
    """
    Real-time driver location tracking
    """
    driver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='locations')
    delivery_request = models.ForeignKey(DeliveryRequest, on_delete=models.CASCADE, related_name='driver_locations', null=True, blank=True)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in meters
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in km/h
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in degrees
    altitude = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # in meters
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'driver_locations'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Location for {self.driver.email} at {self.timestamp}"


class DeliveryZone(models.Model):
    """
    Delivery zones for pricing and availability
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Zone boundaries (simplified as center point and radius)
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_km = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Pricing
    base_delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_fee_per_km = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Availability
    is_active = models.BooleanField(default=True)
    delivery_hours = models.JSONField(default=dict, blank=True)  # {"monday": {"start": "09:00", "end": "18:00"}}
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'delivery_zones'
    
    def __str__(self):
        return self.name
    
    def is_within_zone(self, latitude, longitude):
        """Check if coordinates are within this delivery zone"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1 = radians(self.center_latitude), radians(self.center_longitude)
        lat2, lon2 = radians(latitude), radians(longitude)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance = 6371 * c  # Earth's radius in km
        
        return distance <= self.radius_km
    
    def calculate_delivery_fee(self, distance_km):
        """Calculate delivery fee based on distance"""
        if distance_km <= 0:
            return self.base_delivery_fee
        
        additional_fee = max(0, distance_km - self.radius_km) * self.additional_fee_per_km
        return self.base_delivery_fee + additional_fee


class DriverSchedule(models.Model):
    """
    Driver availability schedule
    """
    driver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    
    # Time slots
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Status
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'driver_schedules'
        unique_together = ['driver', 'date']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.driver.email} - {self.date} ({self.start_time} - {self.end_time})"


class DeliveryRating(models.Model):
    """
    Customer ratings for delivery service
    """
    delivery_request = models.OneToOneField(DeliveryRequest, on_delete=models.CASCADE, related_name='rating')
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='delivery_ratings_given')
    driver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='delivery_ratings_received')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MinValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    
    # Rating categories
    delivery_speed = models.IntegerField(validators=[MinValueValidator(1), MinValueValidator(5)], null=True, blank=True)
    driver_communication = models.IntegerField(validators=[MinValueValidator(1), MinValueValidator(5)], null=True, blank=True)
    package_condition = models.IntegerField(validators=[MinValueValidator(1), MinValueValidator(5)], null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'delivery_ratings'
    
    def __str__(self):
        return f"Rating {self.rating}/5 for delivery {self.delivery_request.tracking_code}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update driver's average rating
        self._update_driver_rating()
    
    def _update_driver_rating(self):
        """Update driver's average rating"""
        ratings = self.driver.delivery_ratings_received.all()
        if ratings.exists():
            avg_rating = sum(rating.rating for rating in ratings) / ratings.count()
            self.driver.rating = round(avg_rating, 2)
            self.driver.save()
