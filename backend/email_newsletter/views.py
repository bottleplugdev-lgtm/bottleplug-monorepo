from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['POST'])
def subscribe(request):
    """Subscribe to newsletter"""
    return Response({'message': 'Newsletter subscription endpoint'})

@api_view(['POST'])
def unsubscribe(request):
    """Unsubscribe from newsletter"""
    return Response({'message': 'Newsletter unsubscription endpoint'})
