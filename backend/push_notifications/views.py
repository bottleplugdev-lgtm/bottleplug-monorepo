from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['POST'])
def send_notification(request):
    """Send push notification"""
    return Response({'message': 'Push notification endpoint'})

@api_view(['POST'])
def register_device(request):
    """Register device for push notifications"""
    return Response({'message': 'Device registration endpoint'})
