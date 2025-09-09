"""
API Tags Configuration for BottlePlug Backend

This module defines all the API tags used in the Swagger documentation
to organize endpoints into logical groups.
"""

# Authentication & User Management
AUTH_TAG = {
    'name': 'auth',
    'description': 'Authentication and user management operations including user registration, login, profile management, and driver management.'
}

# Products
PRODUCTS_TAG = {
    'name': 'products',
    'description': 'Product catalog management including categories, products, variants, and product information.'
}

# Stock
STOCK_TAG = {
    'name': 'stock',
    'description': 'Inventory and stock management including stock levels, inventory logs, and stock updates.'
}

# Orders
ORDERS_TAG = {
    'name': 'orders',
    'description': 'Order management, shopping cart, wishlist, and product reviews.'
}

# Events
EVENTS_TAG = {
    'name': 'events',
    'description': 'Event management and RSVP functionality.'
}

# Newsletter
NEWSLETTER_TAG = {
    'name': 'newsletter',
    'description': 'Newsletter subscription management and email marketing campaigns.'
}

# Deliveries
DELIVERIES_TAG = {
    'name': 'deliveries',
    'description': 'Delivery management, driver locations, delivery zones, schedules, and ratings.'
}

# Analytics
ANALYTICS_TAG = {
    'name': 'analytics',
    'description': 'Analytics and metrics collection including user metrics, product metrics, order metrics, delivery metrics, revenue metrics, and search analytics.'
}

# All tags for easy import
ALL_TAGS = [
    AUTH_TAG,
    PRODUCTS_TAG,
    STOCK_TAG,
    ORDERS_TAG,
    EVENTS_TAG,
    NEWSLETTER_TAG,
    DELIVERIES_TAG,
    ANALYTICS_TAG,
]

# Tag mapping for different app modules
TAG_MAPPING = {
    'users': AUTH_TAG,
    'products': PRODUCTS_TAG,
    'orders': ORDERS_TAG,
    'deliveries': DELIVERIES_TAG,
    'analytics': ANALYTICS_TAG,
    'event_management': EVENTS_TAG,
    'events': EVENTS_TAG,
    'email_newsletter': NEWSLETTER_TAG,
    'newsletter': NEWSLETTER_TAG,
} 