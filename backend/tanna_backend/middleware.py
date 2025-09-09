import logging
import time
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class CORSHeadersMiddleware:
    """
    Custom CORS middleware for additional headers
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add custom CORS headers
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        return response


class ErrorHandlingMiddleware:
    """
    Custom error handling middleware
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'message': str(e) if settings.DEBUG else 'Something went wrong'
            }, status=500)


class RequestLoggingMiddleware:
    """
    Log all requests for debugging
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.path}")
        
        response = self.get_response(request)
        
        # Log response time
        duration = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {duration:.2f}s")
        
        return response 