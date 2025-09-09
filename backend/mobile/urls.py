from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.MobileProductViewSet, basename='mobile-products')
router.register(r'orders', views.MobileOrderViewSet, basename='mobile-orders')

urlpatterns = [
    path('', include(router.urls)),
    path('app-config/', views.MobileAppConfigView.as_view(), name='mobile-config'),
    path('push-tokens/', views.PushTokenView.as_view(), name='push-tokens'),
]