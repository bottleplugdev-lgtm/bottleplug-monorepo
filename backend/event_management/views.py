from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def event_list(request):
    """List all events"""
    return Response({'message': 'Events list endpoint'})

@api_view(['GET'])
def event_detail(request, event_id):
    """Get event details"""
    return Response({'message': f'Event {event_id} details'})
