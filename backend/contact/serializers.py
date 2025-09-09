from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    responded_by = serializers.ReadOnlyField(source='responded_by.email')
    full_name = serializers.ReadOnlyField()
    display_subject = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()
    is_resolved = serializers.ReadOnlyField()
    response_time = serializers.ReadOnlyField()
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'subject', 'subject_custom', 'display_subject', 'message',
            'status', 'priority', 'responded_at', 'response_message',
            'responded_by', 'created_at', 'updated_at', 'ip_address',
            'user_agent', 'referrer', 'subscribe_newsletter',
            'is_new', 'is_resolved', 'response_time'
        ]
        read_only_fields = [
            'status', 'priority', 'responded_at', 'response_message',
            'responded_by', 'created_at', 'updated_at', 'ip_address',
            'user_agent', 'referrer'
        ]

class ContactMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'subject',
            'subject_custom', 'message', 'subscribe_newsletter'
        ]
    
    def validate(self, data):
        # If subject is 'other', subject_custom is required
        if data.get('subject') == 'other' and not data.get('subject_custom'):
            raise serializers.ValidationError("Please specify a custom subject.")
        
        return data

class ContactMessageResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['response_message']
    
    def validate_response_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Response message is required.")
        return value 