from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def mobile_config(request):
    """Get mobile app configuration"""
    return Response({'message': 'Mobile app configuration endpoint'})
