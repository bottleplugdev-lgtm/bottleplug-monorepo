from django.contrib import admin
from .models import (
    PaymentMethod, PaymentTransaction, PaymentWebhook, 
    PaymentRefund, PaymentPlan, PaymentSubscription, PaymentReceipt
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'payment_type', 'is_active', 'country_code', 'currency', 'min_amount', 'max_amount']
    list_filter = ['payment_type', 'is_active', 'country_code', 'currency']
    search_fields = ['name', 'flutterwave_code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'reference', 'transaction_type', 'status', 'amount', 
        'currency', 'customer_name', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'currency', 'created_at', 'paid_at']
    search_fields = ['transaction_id', 'reference', 'customer_name', 'customer_email']
    readonly_fields = [
        'transaction_id', 'reference', 'flutterwave_reference', 'net_amount', 
        'created_at', 'updated_at', 'paid_at', 'expired_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'reference', 'flutterwave_reference', 'transaction_type', 'status')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'fee', 'net_amount', 'payment_method', 'payment_type')
        }),
        ('Related Entities', {
            'fields': ('order', 'invoice', 'event', 'receipt'),
            'classes': ('collapse',)
        }),
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Payment URLs', {
            'fields': ('payment_url', 'redirect_url', 'callback_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'expired_at'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('description', 'metadata', 'flutterwave_response', 'flutterwave_webhook_data'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ['webhook_id', 'transaction', 'event_type', 'processed', 'received_at']
    list_filter = ['event_type', 'processed', 'received_at']
    search_fields = ['webhook_id', 'transaction__transaction_id']
    readonly_fields = ['webhook_id', 'received_at', 'processed_at']
    ordering = ['-received_at']


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id', 'original_transaction', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = ['refund_id', 'reference', 'original_transaction__transaction_id']
    readonly_fields = ['refund_id', 'reference', 'created_at', 'processed_at']
    ordering = ['-created_at']


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'currency', 'interval', 'interval_count', 'is_active']
    list_filter = ['is_active', 'currency', 'interval']
    search_fields = ['name', 'description', 'flutterwave_plan_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(PaymentSubscription)
class PaymentSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'subscription_id', 'customer', 'plan', 'status', 'start_date', 
        'next_payment_date', 'flutterwave_subscription_id'
    ]
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['subscription_id', 'customer__email', 'plan__name']
    readonly_fields = ['subscription_id', 'flutterwave_subscription_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('subscription_id', 'customer', 'plan', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'next_payment_date')
        }),
        ('Flutterwave Integration', {
            'fields': ('flutterwave_subscription_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'transaction', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['receipt_number', 'transaction__transaction_id', 'customer_email', 'customer_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
