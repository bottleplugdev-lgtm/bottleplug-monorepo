from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model that supports Firebase authentication
    and user types from the analyzed projects (customer, driver, admin)
    """
    
    USER_TYPES = [
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    firebase_email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    # Driver fields
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_deliveries = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    current_status = models.CharField(max_length=20, default='offline')
    # Customer fields
    saved_addresses = models.JSONField(default=list, blank=True)
    default_payment_method = models.CharField(max_length=50, blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # Push notification fields
    push_token = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=20, choices=[('android', 'Android'), ('ios', 'iOS')], blank=True)
    # Role fields
    is_staff = models.BooleanField(default=False, null=True, blank=True)
    is_admin = models.BooleanField(default=False, null=True, blank=True)
    is_worker = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_driver(self):
        return self.user_type == 'driver'
    
    @property
    def is_customer(self):
        return self.user_type == 'customer'
    
    @property
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def save(self, *args, **kwargs):
        # Set username to email if not provided
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'users'


class UserSession(models.Model):
    """
    Track user sessions for analytics and security
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_token = models.TextField(unique=True)  # Changed to TextField for longer Firebase tokens
    device_info = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'user_sessions'
    
    def __str__(self):
        return f"Session for {self.user.email} - {self.created_at}"
