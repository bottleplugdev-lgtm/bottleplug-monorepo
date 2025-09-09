from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subscriptions', views.NewsletterSubscriptionViewSet, basename='subscription')
router.register(r'campaigns', views.NewsletterCampaignViewSet, basename='campaign')

urlpatterns = [
    path('', include(router.urls)),
] 