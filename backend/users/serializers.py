from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    
    is_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff', 'is_admin']
        read_only_fields = ['id', 'username', 'email', 'user_type', 'is_active', 'is_staff', 'is_admin']
    
    def get_is_admin(self, obj):
        """Return whether the user is an admin based on user_type or is_superuser"""
        return obj.is_admin_user or obj.is_superuser


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer for detailed profile information"""
    
    full_name = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    displayName = serializers.SerializerMethodField()
    uid = serializers.SerializerMethodField()
    
    # Additional computed fields for frontend compatibility
    is_worker = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    default_payment_method = serializers.SerializerMethodField()
    saved_addresses = serializers.SerializerMethodField()
    wallet_balance = serializers.SerializerMethodField()
    total_deliveries = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'profile_image', 'profile_image_url', 'address',
            'bio', 'user_type', 'is_verified', 'date_of_birth', 'is_staff',
            'is_admin', 'is_active', 'created_at', 'updated_at', 'latitude',
            'longitude', 'rating', 'displayName', 'uid', 'is_worker', 
            'is_available', 'current_status', 'default_payment_method',
            'saved_addresses', 'wallet_balance', 'total_deliveries'
        ]
        read_only_fields = ['id', 'username', 'email', 'user_type', 'is_verified', 'is_staff', 'is_admin', 'is_active', 'created_at', 'updated_at', 'displayName', 'uid', 'is_worker', 'is_available', 'current_status', 'default_payment_method', 'saved_addresses', 'wallet_balance', 'total_deliveries']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
    
    def get_is_admin(self, obj):
        """Return whether the user is an admin based on user_type or is_superuser"""
        return obj.is_admin_user or obj.is_superuser
    
    def get_displayName(self, obj):
        """Return display name for frontend compatibility"""
        return obj.get_full_name() or obj.email
    
    def get_uid(self, obj):
        """Return Firebase UID for frontend compatibility"""
        return obj.firebase_uid
    
    def get_is_worker(self, obj):
        """Return whether user is a worker (driver)"""
        return obj.user_type == 'driver'
    
    def get_is_available(self, obj):
        """Return availability status (for drivers)"""
        return obj.is_active and obj.user_type == 'driver'
    
    def get_current_status(self, obj):
        """Return current status"""
        return 'active' if obj.is_active else 'inactive'
    
    def get_default_payment_method(self, obj):
        """Return default payment method (placeholder)"""
        return None
    
    def get_saved_addresses(self, obj):
        """Return saved addresses (placeholder)"""
        return []
    
    def get_wallet_balance(self, obj):
        """Return wallet balance (placeholder)"""
        return 0.0
    
    def get_total_deliveries(self, obj):
        """Return total deliveries (for drivers)"""
        return 0


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'address', 'bio',
            'date_of_birth', 'profile_image'
        ]
    
    def validate_first_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value.strip() if value else value
    
    def validate_last_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        return value.strip() if value else value
    
    def validate_phone_number(self, value):
        if value:
            # Basic phone number validation for Uganda
            import re
            # Remove all non-digit characters
            digits_only = re.sub(r'\D', '', value)
            # Check if it's a valid Uganda phone number (10 digits starting with 7)
            if not re.match(r'^7\d{9}$', digits_only):
                raise serializers.ValidationError("Please enter a valid Uganda phone number (e.g., 700000000).")
        return value
    
    def validate_bio(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("Bio must be less than 500 characters.")
        return value