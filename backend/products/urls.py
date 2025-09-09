from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'variants', views.ProductVariantViewSet)
router.register(r'inventory-logs', views.InventoryLogViewSet)
router.register(r'measurements', views.ProductMeasurementViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 