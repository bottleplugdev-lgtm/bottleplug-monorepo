from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.AnalyticsEventViewSet)
router.register(r'user-metrics', views.UserMetricsViewSet)
router.register(r'product-metrics', views.ProductMetricsViewSet)
router.register(r'order-metrics', views.OrderMetricsViewSet)
router.register(r'delivery-metrics', views.DeliveryMetricsViewSet)
router.register(r'revenue-metrics', views.RevenueMetricsViewSet)
router.register(r'search-analytics', views.SearchAnalyticsViewSet)
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
] 