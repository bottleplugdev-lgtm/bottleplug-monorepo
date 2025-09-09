from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type', 
            'is_read', 'data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'user', 'title', 'message', 'notification_type', 'data'
        ]


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notifications"""
    
    class Meta:
        model = Notification
        fields = ['is_read'] 