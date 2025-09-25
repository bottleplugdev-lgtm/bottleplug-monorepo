from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'drivers', views.DriverViewSet, basename='driver')
router.register(r'sessions', views.UserSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.FirebaseLoginView.as_view(), name='firebase-login'),
    path('debug-mobile-auth/', views.debug_mobile_auth, name='debug-mobile-auth'),
    # Add other endpoints as needed
]
