from django.urls import path
from . import views

app_name = 'email_newsletter'

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
] 