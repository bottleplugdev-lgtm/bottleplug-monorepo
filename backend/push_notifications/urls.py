from django.urls import path
from . import views

app_name = 'push_notifications'

urlpatterns = [
    path('send/', views.send_notification, name='send_notification'),
    path('register/', views.register_device, name='register_device'),
] 