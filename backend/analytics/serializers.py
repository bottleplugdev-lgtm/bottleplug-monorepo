from rest_framework import serializers
from .models import (
    AnalyticsEvent, UserMetrics, ProductMetrics, OrderMetrics,
    DeliveryMetrics, RevenueMetrics, SearchAnalytics
)


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsEvent model"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'event_type', 'user', 'user_email', 'content_type', 'object_id',
            'event_data', 'session_id', 'user_agent', 'ip_address', 'latitude',
            'longitude', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AnalyticsEventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating analytics events"""
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'event_type', 'content_type', 'object_id', 'event_data', 'session_id',
            'user_agent', 'ip_address', 'latitude', 'longitude'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        validated_data['user'] = user
        return AnalyticsEvent.objects.create(**validated_data)


class UserMetricsSerializer(serializers.ModelSerializer):
    """Serializer for UserMetrics model"""
    
    class Meta:
        model = UserMetrics
        fields = [
            'id', 'date', 'total_users', 'new_users', 'active_users', 'returning_users',
            'customers', 'drivers', 'admins', 'total_sessions', 'avg_session_duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductMetricsSerializer(serializers.ModelSerializer):
    """Serializer for ProductMetrics model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductMetrics
        fields = [
            'id', 'date', 'product', 'product_name', 'views', 'unique_views',
            'add_to_cart_count', 'purchase_count', 'revenue', 'new_reviews',
            'avg_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderMetricsSerializer(serializers.ModelSerializer):
    """Serializer for OrderMetrics model"""
    
    class Meta:
        model = OrderMetrics
        fields = [
            'id', 'date', 'total_orders', 'new_orders', 'completed_orders',
            'cancelled_orders', 'total_revenue', 'avg_order_value', 'cash_payments',
            'card_payments', 'mobile_money_payments', 'wallet_payments',
            'conversion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeliveryMetricsSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryMetrics model"""
    
    class Meta:
        model = DeliveryMetrics
        fields = [
            'id', 'date', 'total_deliveries', 'new_deliveries', 'completed_deliveries',
            'cancelled_deliveries', 'avg_delivery_time', 'avg_delivery_distance',
            'total_delivery_fees', 'avg_delivery_fee', 'active_drivers',
            'avg_driver_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RevenueMetricsSerializer(serializers.ModelSerializer):
    """Serializer for RevenueMetrics model"""
    
    class Meta:
        model = RevenueMetrics
        fields = [
            'id', 'period_type', 'period_start', 'period_end', 'total_revenue',
            'product_revenue', 'delivery_revenue', 'total_costs', 'gross_profit',
            'profit_margin', 'revenue_growth', 'order_growth', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SearchAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for SearchAnalytics model"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = SearchAnalytics
        fields = [
            'id', 'query', 'user', 'user_email', 'results_count', 'clicked_results',
            'search_time', 'is_successful', 'category_filter', 'price_filter',
            'sort_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SearchAnalyticsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating search analytics"""
    
    class Meta:
        model = SearchAnalytics
        fields = [
            'query', 'results_count', 'clicked_results', 'search_time',
            'is_successful', 'category_filter', 'price_filter', 'sort_by'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        validated_data['user'] = user
        return SearchAnalytics.objects.create(**validated_data)


class AnalyticsFilterSerializer(serializers.Serializer):
    """Serializer for analytics filtering"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    event_type = serializers.CharField(max_length=50, required=False)
    user_id = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)
    period_type = serializers.ChoiceField(choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], required=False)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    # User stats
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    
    # Product stats
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    
    # Order stats
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    completed_orders_today = serializers.IntegerField()
    total_revenue_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Delivery stats
    total_deliveries = serializers.IntegerField()
    pending_deliveries = serializers.IntegerField()
    completed_deliveries_today = serializers.IntegerField()
    active_drivers = serializers.IntegerField()
    
    # Growth stats
    revenue_growth = serializers.DecimalField(max_digits=5, decimal_places=2)
    order_growth = serializers.DecimalField(max_digits=5, decimal_places=2)
    user_growth = serializers.DecimalField(max_digits=5, decimal_places=2)


class RevenueChartSerializer(serializers.Serializer):
    """Serializer for revenue chart data"""
    period = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()
    customers = serializers.IntegerField()


class ProductPerformanceSerializer(serializers.Serializer):
    """Serializer for product performance data"""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    views = serializers.IntegerField()
    sales = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2)


class TopSearchTermsSerializer(serializers.Serializer):
    """Serializer for top search terms"""
    query = serializers.CharField()
    count = serializers.IntegerField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class EventTrackingSerializer(serializers.Serializer):
    """Serializer for event tracking"""
    event_type = serializers.CharField()
    event_data = serializers.JSONField(required=False)
    session_id = serializers.CharField(required=False)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False) 