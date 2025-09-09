from rest_framework import serializers
from .models import Event, RSVP
from django.contrib.auth import get_user_model

User = get_user_model()

class EventSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    is_upcoming = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    is_cancelled = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'status',
            'start_date', 'end_date', 'location_name', 'address',
            'city', 'state', 'zip_code', 'max_capacity', 'current_attendees',
            'price', 'member_price', 'featured_wines', 'food_pairings',
            'dress_code', 'age_requirement', 'image', 'gallery',
            'created_by', 'created_at', 'updated_at', 'slug', 'meta_description',
            'is_upcoming', 'is_full', 'available_spots', 'is_cancelled', 'is_completed'
        ]
        read_only_fields = ['current_attendees', 'created_by', 'created_at', 'updated_at']

class EventListSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    is_upcoming = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'event_type', 'status', 'start_date', 'end_date',
            'location_name', 'city', 'state', 'max_capacity', 'current_attendees',
            'price', 'member_price', 'image', 'created_by', 'slug',
            'is_upcoming', 'is_full', 'available_spots'
        ]

class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    event_title = serializers.ReadOnlyField(source='event.title')
    is_confirmed = serializers.ReadOnlyField()
    is_cancelled = serializers.ReadOnlyField()
    is_attended = serializers.ReadOnlyField()
    
    class Meta:
        model = RSVP
        fields = [
            'id', 'event', 'event_title', 'user', 'status', 'guest_count',
            'guest_names', 'dietary_restrictions', 'special_requests',
            'amount_paid', 'payment_method', 'payment_status',
            'created_at', 'updated_at', 'confirmed_at', 'cancelled_at',
            'is_confirmed', 'is_cancelled', 'is_attended'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'confirmed_at', 'cancelled_at']

class RSVPCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = [
            'event', 'guest_count', 'guest_names', 'dietary_restrictions',
            'special_requests'
        ]
    
    def validate_event(self, value):
        if value.is_full:
            raise serializers.ValidationError("This event is full.")
        if value.is_cancelled:
            raise serializers.ValidationError("This event has been cancelled.")
        if value.is_completed:
            raise serializers.ValidationError("This event has already ended.")
        return value
    
    def validate_guest_count(self, value):
        if value < 1:
            raise serializers.ValidationError("Guest count must be at least 1.")
        return value

class RSVPUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = [
            'status', 'guest_count', 'guest_names', 'dietary_restrictions',
            'special_requests', 'amount_paid', 'payment_method', 'payment_status'
        ]
    
    def validate_status(self, value):
        instance = self.instance
        if instance and instance.status == 'attended' and value != 'attended':
            raise serializers.ValidationError("Cannot change status of an attended RSVP.")
        return value

class EventDetailSerializer(EventSerializer):
    rsvps = RSVPSerializer(many=True, read_only=True)
    rsvp_count = serializers.SerializerMethodField()
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['rsvps', 'rsvp_count']
    
    def get_rsvp_count(self, obj):
        return obj.rsvps.count() 