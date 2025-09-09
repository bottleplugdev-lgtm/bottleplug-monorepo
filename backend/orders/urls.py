from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet)
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r'reviews', views.ReviewViewSet)
router.register(r'receipts', views.OrderReceiptViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'delivery-tracking', views.DeliveryTrackingViewSet, basename='delivery-tracking')

urlpatterns = [
    path('', include(router.urls)),
] 