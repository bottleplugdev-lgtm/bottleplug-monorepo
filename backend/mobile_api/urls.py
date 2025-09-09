from django.urls import path
from . import views

app_name = 'mobile_api'

urlpatterns = [
    path('config/', views.mobile_config, name='mobile_config'),
] 