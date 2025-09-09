from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from django.db.models import Q


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter notifications for the current user"""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for the current user"""
        try:
            Notification.objects.filter(
                user=request.user,
                is_read=False
            ).update(is_read=True)
            return Response({'message': 'All notifications marked as read'})
        except Exception as e:
            return Response(
                {'error': 'Failed to mark notifications as read'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read"""
        try:
            notification = self.get_object()
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'})
        except Exception as e:
            return Response(
                {'error': 'Failed to mark notification as read'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        try:
            count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
            return Response({'unread_count': count})
        except Exception as e:
            return Response(
                {'error': 'Failed to get unread count'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 