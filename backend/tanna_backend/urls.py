"""
URL configuration for tanna_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .api_tags import ALL_TAGS
from .health_check import health_check

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="BottlePlug API",
        default_version='v1',
        description="API documentation for BottlePlug backend - Alcohol delivery and e-commerce platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@bottleplug.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health check endpoint
    path('api/health/', health_check, name='health_check'),
    
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api-auth/', include('rest_framework.urls')),
    
    # API endpoints
    path('api/v1/', include([
        path('auth/', include('users.urls')),
        path('products/', include('products.urls')),
        path('orders/', include('orders.urls')),
        path('deliveries/', include('deliveries.urls')),
        path('analytics/', include('analytics.urls')),
        path('events/', include('events.urls')),  # Use events app instead of event_management
        path('newsletter/', include('email_newsletter.urls')),
        path('contact/', include('contact_form.urls')),
        path('notifications/', include('push_notifications.urls')),
        path('mobile/', include('mobile_api.urls')),
        path('payments/', include('payments.urls')),
        path('finance/', include('expenses.urls')),
        path('expenses/', include('expenses.urls')),
        # Keep event_management for admin interface
        path('event-mgmt/', include('event_management.urls')),
    ])),
    
    # Alternative shorter paths for easier access
    path('auth/', include('users.urls')),  # Direct access without api/v1 prefix
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
