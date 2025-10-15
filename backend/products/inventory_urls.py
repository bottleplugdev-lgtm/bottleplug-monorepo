from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .inventory_views import (
    InventoryViewSet, StockMovementViewSet, 
    PreOrderViewSet, EnhancedWishlistViewSet
)

# Create router for inventory endpoints
router = DefaultRouter()
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movements')
router.register(r'pre-orders', PreOrderViewSet, basename='pre-orders')
router.register(r'enhanced-wishlist', EnhancedWishlistViewSet, basename='enhanced-wishlist')

urlpatterns = [
    path('', include(router.urls)),
]
