from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'is_active']
        read_only_fields = ['id', 'username', 'email', 'user_type', 'is_active']


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer for detailed profile information"""
    
    full_name = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'profile_image', 'profile_image_url', 'address',
            'bio', 'user_type', 'is_verified', 'date_of_birth',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'email', 'user_type', 'is_verified', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None


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