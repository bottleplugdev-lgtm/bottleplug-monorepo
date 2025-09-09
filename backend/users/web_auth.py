from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class WebTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication for web API access using an unexpirable token.
    This allows the frontend to access product data without user authentication.
    """
    
    def authenticate(self, request):
        # Get the web token from settings
        web_token = getattr(settings, 'WEB_API_TOKEN', 'bottleplug-web-token-2024')
        
        # Check for the token in headers
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        if token == web_token:
            # Return a special user for web access
            # This allows both anonymous browsing and signed-in user access
            return (WebUser(), None)
            
        return None
    
    def authenticate_header(self, request):
        return 'Bearer realm="api"'

class WebUser:
    """
    A special user class for web API access.
    This user has limited permissions and is used for product browsing.
    """
    
    def __init__(self):
        self.is_authenticated = True
        self.is_anonymous = False
        self.pk = 1  # Give it a valid primary key
        self.id = 1  # Also set id for compatibility
        self.username = 'web_user'
        self.email = 'web@bottleplug.com'
        self.user_type = 'web'
        self.is_customer = True
        self.is_driver = False
        
    def has_perm(self, perm, obj=None):
        # Web user can access product data and basic user actions
        allowed_perms = [
            'products.view_product', 
            'products.view_category',
            'orders.view_order',
            'orders.add_order',
            'orders.view_cart',
            'orders.add_cart',
            'orders.change_cart',
            'orders.delete_cart',
            'orders.view_wishlist',
            'orders.add_wishlist',
            'orders.change_wishlist',
            'orders.delete_wishlist',
            'events.view_event',
            'events.view_rsvp',
            'events.add_rsvp',
            'events.change_rsvp',
            'events.delete_rsvp',
            'payments.view_paymentmethod',
            'payments.add_paymentmethod',
            'payments.view_transaction',
            'payments.add_transaction'
        ]
        if perm in allowed_perms:
            return True
        return False
        
    def has_module_perms(self, app_label):
        # Web user can access multiple apps for full functionality
        allowed_apps = ['products', 'orders', 'events', 'payments', 'deliveries', 'notifications']
        if app_label in allowed_apps:
            return True
        return False
        
    def is_staff(self):
        return False
        
    def is_superuser(self):
        return False
