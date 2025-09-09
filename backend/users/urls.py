from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'drivers', views.DriverViewSet, basename='driver')
router.register(r'sessions', views.UserSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/login/', views.admin_login, name='admin-login'),
    path('location/', views.UserLocationView.as_view(), name='user-location'),
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('create-firebase-user/', views.create_firebase_user, name='create-firebase-user'),
    path('migrate-to-firebase/', views.migrate_all_users_to_firebase, name='migrate-to-firebase'),
    path('firebase-debug/', views.firebase_debug, name='firebase-debug'),
]
