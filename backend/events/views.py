from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Event, RSVP
import logging

logger = logging.getLogger(__name__)
from .serializers import (
    EventSerializer, EventListSerializer, EventDetailSerializer,
    RSVPSerializer, RSVPCreateSerializer, RSVPUpdateSerializer
)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(tags=['events'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def _handle_gallery_upload(self, request, event: Event):
        """Save multiple uploaded gallery images and set event.gallery to their URLs."""
        try:
            files = request.FILES.getlist('gallery')
        except Exception:
            files = []
        logger.info("Gallery upload: received %s files", len(files))
        if not files:
            return []

        from django.core.files.storage import default_storage

        saved_urls = []
        for upload in files:
            logger.info("Saving gallery file: %s (%s bytes)", getattr(upload, 'name', 'unknown'), getattr(upload, 'size', 'n/a'))
            # Use timestamp to help uniqueness; storage will still ensure unique names
            filename = f"events/gallery/{timezone.now().strftime('%Y%m%d%H%M%S')}_{upload.name}"
            saved_path = default_storage.save(filename, upload)
            saved_urls.append(default_storage.url(saved_path))

        # Replace gallery with uploaded images list
        event.gallery = saved_urls
        event.save(update_fields=['gallery'])
        logger.info("Gallery saved for event %s: %s", event.id, saved_urls)
        return saved_urls

    @swagger_auto_schema(tags=['events'])
    def create(self, request, *args, **kwargs):
        # Use serializer to create base event first (image handled by DRF)
        try:
            logger.info("Creating event with data keys: %s", list(request.data.keys()))
            # DRF JSONField cannot accept uploaded files; strip gallery before validation
            data = request.data.copy()
            if hasattr(data, 'setlist'):
                try:
                    data.setlist('gallery', [])
                except Exception:
                    data.pop('gallery', None)
            else:
                data.pop('gallery', None)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            event = serializer.save(created_by=request.user)

            # Process any gallery files
            self._handle_gallery_upload(request, event)

            output = EventDetailSerializer(event, context=self.get_serializer_context())
            headers = self.get_success_headers(output.data)
            return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as ve:
            # Log and surface serializer errors
            logger.warning("Event creation validation error: %s", getattr(ve, 'detail', ve))
            return Response(getattr(ve, 'detail', {'detail': 'Validation error'}), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Unexpected error creating event: %s", str(e))
            return Response({'detail': 'Unexpected error creating event'}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['events'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['events'])
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Strip gallery from data so JSONField validation does not see uploaded files
        data = request.data.copy()
        if hasattr(data, 'setlist'):
            try:
                data.setlist('gallery', [])
            except Exception:
                data.pop('gallery', None)
        else:
            data.pop('gallery', None)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        self._handle_gallery_upload(request, event)

        output = EventDetailSerializer(event, context=self.get_serializer_context())
        return Response(output.data)
    
    @swagger_auto_schema(tags=['events'])
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['events'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer
    
    def get_queryset(self):
        queryset = Event.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by event type
        event_type = self.request.query_params.get('event_type', None)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(
                Q(city__icontains=location) | 
                Q(state__icontains=location) |
                Q(location_name__icontains=location)
            )
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location_name__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Get all RSVPs for a specific event"
    )
    @action(detail=True, methods=['get'])
    def rsvps(self, request, pk=None):
        """Get all RSVPs for a specific event"""
        event = self.get_object()
        rsvps = event.rsvps.all()
        serializer = RSVPSerializer(rsvps, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Get upcoming events"
    )
    @action(detail=True, methods=['get'])
    def upcoming(self, request, pk=None):
        """Get upcoming events"""
        queryset = self.get_queryset().filter(
            start_date__gt=timezone.now(),
            status='published'
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Get featured upcoming events"
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured upcoming events"""
        queryset = self.get_queryset().filter(
            start_date__gt=timezone.now(),
            status='published'
        ).order_by('start_date')[:6]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Cancel an event"
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an event"""
        event = self.get_object()
        
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can cancel events.")
        
        if event.is_cancelled:
            raise ValidationError("This event is already cancelled.")
        
        if event.is_completed:
            raise ValidationError("Cannot cancel a completed event.")
        
        event.status = 'cancelled'
        event.save()
        
        return Response({
            'message': 'Event cancelled successfully.',
            'status': 'cancelled'
        })

class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['events'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['events'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['events'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['events'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['events'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['events'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RSVPCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RSVPUpdateSerializer
        return RSVPSerializer
    
    def get_queryset(self):
        # Users can only see their own RSVPs, staff can see all
        if self.request.user.is_staff:
            return RSVP.objects.all()
        return RSVP.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        event = serializer.validated_data['event']
        
        # Check if user already has an RSVP for this event
        existing_rsvp = RSVP.objects.filter(
            event=event,
            user=self.request.user
        ).first()
        
        if existing_rsvp:
            raise ValidationError("You have already RSVP'd for this event.")
        
        # Check if event is full
        if event.is_full:
            raise ValidationError("This event is full.")
        
        # Check if event is cancelled or completed
        if event.is_cancelled:
            raise ValidationError("This event has been cancelled.")
        
        if event.is_completed:
            raise ValidationError("This event has already ended.")
        
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        rsvp = self.get_object()
        
        # Only allow users to update their own RSVPs or staff to update any
        if not self.request.user.is_staff and rsvp.user != self.request.user:
            raise PermissionDenied("You can only update your own RSVPs.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow users to cancel their own RSVPs or staff to cancel any
        if not self.request.user.is_staff and instance.user != self.request.user:
            raise PermissionDenied("You can only cancel your own RSVPs.")
        
        instance.status = 'cancelled'
        instance.save()
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Confirm an RSVP"
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an RSVP"""
        rsvp = self.get_object()
        
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can confirm RSVPs.")
        
        if rsvp.status == 'confirmed':
            raise ValidationError("This RSVP is already confirmed.")
        
        if rsvp.status == 'cancelled':
            raise ValidationError("Cannot confirm a cancelled RSVP.")
        
        rsvp.status = 'confirmed'
        rsvp.confirmed_at = timezone.now()
        rsvp.save()
        
        return Response({
            'message': 'RSVP confirmed successfully.',
            'status': 'confirmed'
        })
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Mark RSVP as attended"
    )
    @action(detail=True, methods=['post'])
    def mark_attended(self, request, pk=None):
        """Mark an RSVP as attended"""
        rsvp = self.get_object()
        
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can mark attendance.")
        
        if rsvp.status != 'confirmed':
            raise ValidationError("Only confirmed RSVPs can be marked as attended.")
        
        rsvp.status = 'attended'
        rsvp.save()
        
        return Response({
            'message': 'Attendance marked successfully.',
            'status': 'attended'
        })
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Get current user's RSVPs"
    )
    @action(detail=False, methods=['get'])
    def my_rsvps(self, request):
        """Get current user's RSVPs"""
        rsvps = RSVP.objects.filter(user=request.user)
        serializer = self.get_serializer(rsvps, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['events'],
        operation_description="Get upcoming RSVPs for current user"
    )
    @action(detail=False, methods=['get'])
    def upcoming_rsvps(self, request):
        """Get current user's upcoming RSVPs"""
        rsvps = RSVP.objects.filter(
            user=request.user,
            event__start_date__gt=timezone.now(),
            event__status='published'
        ).exclude(status='cancelled')
        serializer = self.get_serializer(rsvps, many=True)
        return Response(serializer.data)
