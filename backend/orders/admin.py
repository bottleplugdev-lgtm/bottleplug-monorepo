from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem, Wishlist, Review, OrderReceipt, Invoice


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'is_pickup']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status', 'payment_method')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'delivery_fee', 'discount', 'total_amount')
        }),
        ('Delivery', {
            'fields': ('is_pickup', 'delivery_address', 'delivery_instructions', 'delivery_person')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'district', 'state', 'postal_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'estimated_delivery_time', 'actual_delivery_time')
        }),
        ('Additional', {
            'fields': ('notes', 'cancellation_reason', 'tracking_data')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product_name']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price']
    list_filter = ['created_at']
    search_fields = ['cart__user__email', 'product__name']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['user__email', 'product__name', 'title']


@admin.register(OrderReceipt)
class OrderReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'order', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['receipt_number', 'customer_name', 'customer_email']
    readonly_fields = ['receipt_number', 'created_at', 'sent_at', 'signed_at', 'delivered_at']
    ordering = ['-created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'customer_name', 'status', 'total_amount', 'balance_due', 'due_date']
    list_filter = ['status', 'payment_terms', 'created_at', 'due_date']
    search_fields = ['invoice_number', 'customer_name', 'customer_email']
    readonly_fields = ['invoice_number', 'created_at', 'sent_at', 'paid_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'order', 'status', 'payment_terms', 'due_date')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_address')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'tax_rate', 'discount_amount', 'total_amount', 'amount_paid', 'balance_due')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_transaction_id', 'payment_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'paid_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'terms_and_conditions', 'company_info'),
            'classes': ('collapse',)
        }),
    )
