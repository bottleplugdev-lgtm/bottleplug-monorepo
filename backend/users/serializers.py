from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'user_type', 'phone_number',
            'profile_image', 'address', 'latitude', 'longitude', 'is_verified',
            'is_staff', 'is_admin', 'is_worker', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with all fields"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'user_type', 'phone_number',
            'profile_image', 'address', 'latitude', 'longitude', 'is_verified',
            'vehicle_type', 'vehicle_number', 'license_number', 'rating',
            'total_deliveries', 'is_available', 'current_status', 'saved_addresses',
            'default_payment_method', 'wallet_balance', 'is_staff', 'is_admin', 
            'is_worker', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'user_type', 'phone_number',
            'profile_image', 'address', 'latitude', 'longitude', 'is_staff',
            'is_admin', 'is_worker', 'password'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates with Firebase authentication"""
    
    class Meta:
        model = User
        fields = [
            'firebase_uid', 'email', 'first_name', 'last_name', 'user_type', 
            'phone_number', 'profile_image', 'address', 'latitude', 'longitude', 
            'is_verified', 'is_active', 'is_staff', 'is_admin', 'is_worker'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Create user with Firebase UID
        user = User.objects.create(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        # Update user profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profiles"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'profile_image',
            'address', 'latitude', 'longitude', 'saved_addresses',
            'default_payment_method', 'is_staff', 'is_admin', 'is_worker'
        ]


class DriverProfileSerializer(serializers.ModelSerializer):
    """Serializer for driver-specific profile updates"""
    
    class Meta:
        model = User
        fields = [
            'vehicle_type', 'vehicle_number', 'license_number',
            'is_available', 'current_status'
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_token', 'device_info', 'ip_address', 'user_agent',
            'is_active', 'created_at', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at']


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    customers_count = serializers.IntegerField()
    drivers_count = serializers.IntegerField()
    admins_count = serializers.IntegerField()


class FirebaseAuthSerializer(serializers.Serializer):
    """Serializer for Firebase authentication"""
    firebase_token = serializers.CharField()
    device_info = serializers.JSONField(required=False)
    ip_address = serializers.IPAddressField(required=False)


class UserLocationSerializer(serializers.Serializer):
    """Serializer for updating user location"""
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    accuracy = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    speed = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    heading = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    altitude = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)


class DriverAvailabilitySerializer(serializers.Serializer):
    """Serializer for driver availability updates"""
    is_available = serializers.BooleanField()
    current_status = serializers.ChoiceField(choices=[
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('busy', 'Busy')
    ])
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)


class WalletTransactionSerializer(serializers.Serializer):
    """Serializer for wallet transactions"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = serializers.ChoiceField(choices=[
        ('credit', 'Credit'),
        ('debit', 'Debit')
    ])
    description = serializers.CharField(max_length=200)
    reference = serializers.CharField(max_length=100, required=False) 