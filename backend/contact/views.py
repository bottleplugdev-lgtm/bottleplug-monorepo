from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from .models import ContactMessage
from .serializers import (
    ContactMessageSerializer, 
    ContactMessageCreateSerializer,
    ContactMessageResponseSerializer
)

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContactMessageCreateSerializer
        elif self.action in ['respond', 'mark_responded']:
            return ContactMessageResponseSerializer
        return ContactMessageSerializer
    
    def get_queryset(self):
        # Users can only see their own messages, staff can see all
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        return ContactMessage.objects.filter(email=self.request.user.email)
    
    def perform_create(self, serializer):
        # Set additional metadata
        serializer.save(
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            referrer=self.request.META.get('HTTP_REFERER', '')
        )
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to a contact message"""
        message = self.get_object()
        
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can respond to messages.")
        
        if message.is_resolved:
            raise ValidationError("This message has already been resolved.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        response_message = serializer.validated_data['response_message']
        message.mark_as_responded(response_message, request.user)
        
        return Response({
            'message': 'Response sent successfully.',
            'status': 'resolved'
        })
    
    @action(detail=True, methods=['post'])
    def mark_in_progress(self, request, pk=None):
        """Mark a message as in progress"""
        message = self.get_object()
        
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can update message status.")
        
        if message.is_resolved:
            raise ValidationError("Cannot mark a resolved message as in progress.")
        
        message.mark_as_in_progress(request.user)
        
        return Response({
            'message': 'Message marked as in progress.',
            'status': 'in_progress'
        })
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a message"""
        message = self.get_object()
        
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can close messages.")
        
        message.close_message(request.user)
        
        return Response({
            'message': 'Message closed successfully.',
            'status': 'closed'
        })
    
    @action(detail=False, methods=['get'])
    def my_messages(self, request):
        """Get current user's contact messages"""
        messages = ContactMessage.objects.filter(email=request.user.email)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages (staff only)"""
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can view unread counts.")
        
        count = ContactMessage.objects.filter(status='new').count()
        return Response({'unread_count': count})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
