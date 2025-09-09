from rest_framework import serializers
from .models import DeliveryRequest, DriverLocation, DeliveryZone, DriverSchedule, DeliveryRating


class DeliveryRequestSerializer(serializers.ModelSerializer):
    """Basic DeliveryRequest serializer"""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    
    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'customer', 'customer_name', 'driver', 'driver_name',
            'pickup_address', 'delivery_address', 'pickup_latitude', 'pickup_longitude',
            'delivery_latitude', 'delivery_longitude', 'status', 'payment_status',
            'tracking_code', 'amount', 'delivery_fee', 'payment_method',
            'estimated_time', 'actual_time', 'distance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tracking_code', 'created_at', 'updated_at']


class DeliveryRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed DeliveryRequest serializer"""
    customer = serializers.SerializerMethodField()
    driver = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryRequest
        fields = [
            'id', 'customer', 'driver', 'pickup_address', 'delivery_address',
            'pickup_latitude', 'pickup_longitude', 'delivery_latitude', 'delivery_longitude',
            'status', 'payment_status', 'tracking_code', 'amount', 'delivery_fee',
            'payment_method', 'estimated_time', 'actual_time', 'distance',
            'created_at', 'updated_at', 'accepted_at', 'picked_up_at', 'delivered_at',
            'cancelled_at', 'notes', 'cancel_reason', 'items', 'customer_signature',
            'driver_signature', 'images'
        ]
        read_only_fields = ['id', 'tracking_code', 'created_at', 'updated_at']
    
    def get_customer(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.customer).data if obj.customer else None
    
    def get_driver(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.driver).data if obj.driver else None


class DeliveryRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating delivery requests"""
    
    class Meta:
        model = DeliveryRequest
        fields = [
            'pickup_address', 'delivery_address', 'pickup_latitude', 'pickup_longitude',
            'delivery_latitude', 'delivery_longitude', 'amount', 'payment_method',
            'notes', 'items'
        ]
    
    def create(self, validated_data):
        customer = self.context['request'].user
        validated_data['customer'] = customer
        return DeliveryRequest.objects.create(**validated_data)


class DeliveryRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating delivery requests"""
    
    class Meta:
        model = DeliveryRequest
        fields = [
            'status', 'payment_status', 'driver', 'estimated_time', 'actual_time',
            'distance', 'notes', 'cancel_reason', 'customer_signature',
            'driver_signature', 'images'
        ]


class DriverLocationSerializer(serializers.ModelSerializer):
    """Serializer for DriverLocation model"""
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    
    class Meta:
        model = DriverLocation
        fields = [
            'id', 'driver', 'driver_name', 'delivery_request', 'latitude', 'longitude',
            'accuracy', 'speed', 'heading', 'altitude', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class DriverLocationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating driver location updates"""
    
    class Meta:
        model = DriverLocation
        fields = [
            'delivery_request', 'latitude', 'longitude', 'accuracy', 'speed',
            'heading', 'altitude'
        ]
    
    def create(self, validated_data):
        driver = self.context['request'].user
        validated_data['driver'] = driver
        return DriverLocation.objects.create(**validated_data)


class DeliveryZoneSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryZone model"""
    
    class Meta:
        model = DeliveryZone
        fields = [
            'id', 'name', 'description', 'center_latitude', 'center_longitude',
            'radius_km', 'base_delivery_fee', 'additional_fee_per_km',
            'minimum_order_amount', 'is_active', 'delivery_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverScheduleSerializer(serializers.ModelSerializer):
    """Serializer for DriverSchedule model"""
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    
    class Meta:
        model = DriverSchedule
        fields = [
            'id', 'driver', 'driver_name', 'date', 'start_time', 'end_time',
            'is_available', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating driver schedules"""
    
    class Meta:
        model = DriverSchedule
        fields = ['date', 'start_time', 'end_time', 'is_available', 'notes']
    
    def create(self, validated_data):
        driver = self.context['request'].user
        validated_data['driver'] = driver
        return DriverSchedule.objects.create(**validated_data)


class DeliveryRatingSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryRating model"""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    delivery_tracking = serializers.CharField(source='delivery_request.tracking_code', read_only=True)
    
    class Meta:
        model = DeliveryRating
        fields = [
            'id', 'delivery_request', 'delivery_tracking', 'customer', 'customer_name',
            'driver', 'driver_name', 'rating', 'comment', 'delivery_speed',
            'driver_communication', 'package_condition', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DeliveryRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating delivery ratings"""
    
    class Meta:
        model = DeliveryRating
        fields = [
            'delivery_request', 'rating', 'comment', 'delivery_speed',
            'driver_communication', 'package_condition'
        ]
    
    def create(self, validated_data):
        customer = self.context['request'].user
        delivery_request = validated_data['delivery_request']
        
        # Verify customer owns this delivery request
        if delivery_request.customer != customer:
            raise serializers.ValidationError("You can only rate your own deliveries")
        
        validated_data['customer'] = customer
        validated_data['driver'] = delivery_request.driver
        
        return DeliveryRating.objects.create(**validated_data)


class DeliveryRequestFilterSerializer(serializers.Serializer):
    """Serializer for delivery request filtering"""
    status = serializers.CharField(max_length=20, required=False)
    payment_status = serializers.CharField(max_length=20, required=False)
    payment_method = serializers.CharField(max_length=50, required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    min_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class DeliveryStatsSerializer(serializers.Serializer):
    """Serializer for delivery statistics"""
    total_deliveries = serializers.IntegerField()
    pending_deliveries = serializers.IntegerField()
    completed_deliveries = serializers.IntegerField()
    cancelled_deliveries = serializers.IntegerField()
    total_delivery_fees = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_delivery_time = serializers.DecimalField(max_digits=5, decimal_places=2)
    avg_delivery_distance = serializers.DecimalField(max_digits=6, decimal_places=2)
    active_drivers = serializers.IntegerField()
    avg_driver_rating = serializers.DecimalField(max_digits=3, decimal_places=2)


class DeliveryZoneCheckSerializer(serializers.Serializer):
    """Serializer for checking delivery zone"""
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class DeliveryFeeCalculatorSerializer(serializers.Serializer):
    """Serializer for calculating delivery fees"""
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    delivery_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False) 