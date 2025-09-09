from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['POST'])
def submit_contact(request):
    """Submit contact form"""
    return Response({'message': 'Contact form submission endpoint'})
