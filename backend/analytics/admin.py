from django.contrib import admin
from .models import (
    AnalyticsEvent, UserMetrics, ProductMetrics, OrderMetrics,
    DeliveryMetrics, RevenueMetrics, SearchAnalytics
)


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_type', 'user', 'created_at', 'session_id']
    list_filter = ['event_type', 'created_at', 'user__user_type']
    search_fields = ['event_type', 'user__email', 'session_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'user', 'session_id', 'created_at')
        }),
        ('Event Data', {
            'fields': ('event_data',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserMetrics)
class UserMetricsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'total_users', 'new_users', 'active_users']
    list_filter = ['date']
    search_fields = ['date']
    ordering = ['-date']
    readonly_fields = ['date']
    
    fieldsets = (
        ('Date Information', {
            'fields': ('date',)
        }),
        ('User Counts', {
            'fields': ('total_users', 'new_users', 'active_users', 'returning_users')
        }),
        ('User Types', {
            'fields': ('customers', 'drivers', 'admins')
        }),
        ('Engagement Metrics', {
            'fields': ('avg_session_duration',)
        }),
    )


@admin.register(ProductMetrics)
class ProductMetricsAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'date', 'views', 'purchase_count', 'revenue']
    list_filter = ['date', 'product__category']
    search_fields = ['product__name', 'product__sku']
    ordering = ['-date']
    readonly_fields = ['date']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'date')
        }),
        ('View Metrics', {
            'fields': ('views', 'unique_views', 'add_to_cart_count')
        }),
        ('Sales Metrics', {
            'fields': ('purchase_count', 'revenue')
        }),
        ('Performance Metrics', {
            'fields': ('avg_rating', 'new_reviews')
        }),
    )


@admin.register(OrderMetrics)
class OrderMetricsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'total_orders', 'total_revenue', 'avg_order_value']
    list_filter = ['date']
    ordering = ['-date']
    readonly_fields = ['date']
    
    fieldsets = (
        ('Date Information', {
            'fields': ('date',)
        }),
        ('Order Metrics', {
            'fields': ('total_orders', 'completed_orders', 'cancelled_orders')
        }),
        ('Revenue Metrics', {
            'fields': ('total_revenue', 'avg_order_value', 'refund_amount')
        }),
        ('Performance Metrics', {
            'fields': ('conversion_rate', 'repeat_customer_rate', 'customer_satisfaction')
        }),
    )


@admin.register(DeliveryMetrics)
class DeliveryMetricsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'total_deliveries', 'completed_deliveries', 'avg_delivery_time']
    list_filter = ['date']
    ordering = ['-date']
    readonly_fields = ['date']
    
    fieldsets = (
        ('Date Information', {
            'fields': ('date',)
        }),
        ('Delivery Metrics', {
            'fields': ('total_deliveries', 'completed_deliveries', 'cancelled_deliveries')
        }),
        ('Performance Metrics', {
            'fields': ('avg_delivery_time', 'on_time_deliveries', 'delivery_success_rate')
        }),
        ('Driver Metrics', {
            'fields': ('active_drivers', 'avg_driver_rating', 'driver_satisfaction')
        }),
    )


@admin.register(RevenueMetrics)
class RevenueMetricsAdmin(admin.ModelAdmin):
    list_display = ['id', 'period_type', 'period_start', 'total_revenue', 'gross_profit']
    list_filter = ['period_type', 'period_start']
    ordering = ['-period_start']
    readonly_fields = ['period_start', 'period_end']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_type', 'period_start', 'period_end')
        }),
        ('Revenue Metrics', {
            'fields': ('total_revenue', 'product_revenue', 'delivery_revenue')
        }),
        ('Cost and Profit', {
            'fields': ('total_costs', 'gross_profit', 'profit_margin')
        }),
        ('Growth Metrics', {
            'fields': ('revenue_growth', 'order_growth')
        }),
    )


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'query', 'created_at', 'results_count', 'is_successful']
    list_filter = ['created_at', 'is_successful', 'user__user_type']
    search_fields = ['query', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Search Information', {
            'fields': ('user', 'query', 'created_at')
        }),
        ('Results Information', {
            'fields': ('results_count', 'clicked_results', 'search_time', 'is_successful')
        }),
        ('Search Context', {
            'fields': ('category_filter', 'price_filter', 'sort_by'),
            'classes': ('collapse',)
        }),
    )
