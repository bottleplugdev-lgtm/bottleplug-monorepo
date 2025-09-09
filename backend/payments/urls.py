from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Payment methods
router.register(r'payment-methods', views.PaymentMethodViewSet)

# Payment transactions
router.register(r'transactions', views.PaymentTransactionViewSet)

# Payment webhooks
router.register(r'webhooks', views.PaymentWebhookViewSet)

# Payment refunds
router.register(r'refunds', views.PaymentRefundViewSet)

# Payment plans
router.register(r'plans', views.PaymentPlanViewSet)

# Payment subscriptions
router.register(r'subscriptions', views.PaymentSubscriptionViewSet)

# Payment receipts
router.register(r'payment_receipts', views.PaymentReceiptViewSet, basename='payment_receipts')

# Flutterwave utilities
router.register(r'flutterwave', views.FlutterwaveUtilityViewSet, basename='flutterwave')

urlpatterns = [
    path('', include(router.urls)),
] 