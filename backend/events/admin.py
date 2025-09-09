from django.contrib import admin
from .models import Event, RSVP

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'status', 'start_date', 'end_date', 'location_name', 'city', 'current_attendees', 'max_capacity', 'price']
    list_filter = ['status', 'event_type', 'start_date', 'city']
    search_fields = ['title', 'description', 'location_name', 'city']
    readonly_fields = ['created_at', 'updated_at', 'current_attendees']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'event_type', 'status', 'slug')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date')
        }),
        ('Location', {
            'fields': ('location_name', 'address', 'city', 'state', 'zip_code')
        }),
        ('Capacity & Pricing', {
            'fields': ('max_capacity', 'current_attendees', 'price', 'member_price')
        }),
        ('Event Details', {
            'fields': ('featured_wines', 'food_pairings', 'dress_code', 'age_requirement')
        }),
        ('Media', {
            'fields': ('image', 'gallery')
        }),
        ('SEO', {
            'fields': ('meta_description',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New event
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'guest_count', 'amount_paid', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'event']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'event__title']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'cancelled_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event', 'user', 'status')
        }),
        ('Guest Information', {
            'fields': ('guest_count', 'guest_names', 'dietary_restrictions', 'special_requests')
        }),
        ('Payment', {
            'fields': ('amount_paid', 'payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
