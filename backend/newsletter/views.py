from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import NewsletterSubscription, NewsletterCampaign
from .serializers import NewsletterSubscriptionSerializer, NewsletterCampaignSerializer

class NewsletterSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(tags=['newsletter'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        # Users can only see their own subscriptions, staff can see all
        if self.request.user.is_staff:
            return NewsletterSubscription.objects.all()
        return NewsletterSubscription.objects.filter(email=self.request.user.email)
    
    @swagger_auto_schema(
        tags=['newsletter'],
        operation_description="Subscribe to newsletter"
    )
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """Subscribe to newsletter"""
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not email:
            raise ValidationError("Email is required.")
        
        try:
            validate_email(email)
        except DjangoValidationError:
            raise ValidationError("Please enter a valid email address.")
        
        # Check if already subscribed
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'source': request.data.get('source', 'website'),
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        
        if not created:
            if subscription.status == 'unsubscribed':
                subscription.reactivate()
                subscription.first_name = first_name
                subscription.last_name = last_name
                subscription.save()
                message = "Welcome back! You have been resubscribed to our newsletter."
            else:
                message = "You are already subscribed to our newsletter."
        else:
            message = "Thank you for subscribing to our newsletter!"
        
        return Response({
            'message': message,
            'email': email,
            'status': subscription.status
        })
    
    @swagger_auto_schema(
        tags=['newsletter'],
        operation_description="Unsubscribe from newsletter"
    )
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        """Unsubscribe from newsletter"""
        email = request.data.get('email')
        
        if not email:
            raise ValidationError("Email is required.")
        
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            subscription.unsubscribe()
            return Response({
                'message': 'You have been unsubscribed from our newsletter.',
                'email': email
            })
        except NewsletterSubscription.DoesNotExist:
            raise ValidationError("This email is not subscribed to our newsletter.")
    
    @swagger_auto_schema(
        tags=['newsletter'],
        operation_description="Resubscribe to newsletter"
    )
    @action(detail=False, methods=['post'])
    def resubscribe(self, request):
        """Resubscribe to newsletter"""
        email = request.data.get('email')
        
        if not email:
            raise ValidationError("Email is required.")
        
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            subscription.reactivate()
            return Response({
                'message': 'Welcome back! You have been resubscribed to our newsletter.',
                'email': email
            })
        except NewsletterSubscription.DoesNotExist:
            raise ValidationError("This email is not in our system.")
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class NewsletterCampaignViewSet(viewsets.ModelViewSet):
    queryset = NewsletterCampaign.objects.all()
    serializer_class = NewsletterCampaignSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @swagger_auto_schema(tags=['newsletter'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['newsletter'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @swagger_auto_schema(
        tags=['newsletter'],
        operation_description="Send newsletter campaign"
    )
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a newsletter campaign"""
        campaign = self.get_object()
        
        if campaign.status != 'draft':
            raise ValidationError("Only draft campaigns can be sent.")
        
        # Here you would integrate with your email service
        # For now, we'll just mark it as sent
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        return Response({
            'message': 'Newsletter campaign sent successfully.',
            'campaign_id': campaign.id
        })
    
    @swagger_auto_schema(
        tags=['newsletter'],
        operation_description="Schedule newsletter campaign"
    )
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a newsletter campaign"""
        campaign = self.get_object()
        scheduled_at = request.data.get('scheduled_at')
        
        if not scheduled_at:
            raise ValidationError("Scheduled date and time is required.")
        
        try:
            scheduled_datetime = timezone.datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            if scheduled_datetime <= timezone.now():
                raise ValidationError("Scheduled time must be in the future.")
        except ValueError:
            raise ValidationError("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS).")
        
        campaign.status = 'scheduled'
        campaign.scheduled_at = scheduled_datetime
        campaign.save()
        
        return Response({
            'message': 'Newsletter campaign scheduled successfully.',
            'scheduled_at': scheduled_at
        })
