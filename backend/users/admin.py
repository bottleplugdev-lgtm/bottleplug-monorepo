from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    
    list_display = [
        'email', 'first_name', 'last_name', 'user_type', 'is_verified',
        'is_active', 'created_at'
    ]
    list_filter = [
        'user_type', 'is_verified', 'is_active', 'created_at'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'profile_image',
                'address', 'latitude', 'longitude', 'is_verified'
            )
        }),
        ('User Type', {
            'fields': ('user_type',)
        }),
        ('Driver Info', {
            'fields': (
                'vehicle_type', 'vehicle_number', 'license_number', 'rating'
            ),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'first_name', 'last_name',
                'user_type', 'phone_number'
            ),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


# UserSession model has been removed - admin configuration removed
