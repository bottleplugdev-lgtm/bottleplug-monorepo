from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
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
    # Additional profile fields
    bio = models.TextField(blank=True, null=True, help_text="User's bio or description")
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email or self.username

    @property
    def is_customer(self):
        return self.user_type == 'customer'
    
    @property
    def is_driver(self):
        return self.user_type == 'driver'
    
    @property
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def save(self, *args, **kwargs):
        # Set username to email if not provided
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email or self.username

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email or self.username