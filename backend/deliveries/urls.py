from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'deliveries', views.DeliveryRequestViewSet)
router.register(r'driver-locations', views.DriverLocationViewSet, basename='driver-location')
router.register(r'delivery-zones', views.DeliveryZoneViewSet)
router.register(r'driver-schedules', views.DriverScheduleViewSet, basename='driver-schedule')
router.register(r'delivery-ratings', views.DeliveryRatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 