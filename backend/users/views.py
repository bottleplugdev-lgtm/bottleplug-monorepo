from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import firebase_admin
from firebase_admin import auth as firebase_auth
import jwt
from django.conf import settings

from .models import User
from .serializers import UserSerializer, UserProfileSerializer, UserProfileUpdateSerializer
from .authentication import FirebaseAuthentication


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [FirebaseAuthentication]

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Handle profile image upload if provided
            if 'profile_image' in request.data:
                profile_image_data = request.data['profile_image']
                if profile_image_data and profile_image_data != 'null':
                    try:
                        # Handle base64 image data
                        if isinstance(profile_image_data, str) and profile_image_data.startswith('data:image'):
                            # Extract base64 data
                            format, imgstr = profile_image_data.split(';base64,')
                            ext = format.split('/')[-1]
                            
                            # Generate unique filename
                            filename = f"profile_{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                            
                            # Save file
                            file_data = ContentFile(base64.b64decode(imgstr))
                            user.profile_image.save(filename, file_data, save=True)
                        else:
                            # Handle direct file upload
                            user.profile_image = profile_image_data
                    except Exception as e:
                        return Response(
                            {'error': f'Failed to process image: {str(e)}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'data': UserProfileSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def upload_profile_image(self, request):
        """Upload profile image"""
        user = request.user
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validate file type
        if not image_file.content_type.startswith('image/'):
            return Response(
                {'error': 'File must be an image'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (5MB max)
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'File size must be less than 5MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate unique filename
            filename = f"profile_{user.id}_{uuid.uuid4().hex[:8]}.{image_file.name.split('.')[-1]}"
            
            # Save file
            user.profile_image.save(filename, image_file, save=True)
            
            return Response({
                'message': 'Profile image uploaded successfully',
                'profile_image_url': user.profile_image.url if user.profile_image else None
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to upload image: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['delete'])
    def delete_profile_image(self, request):
        """Delete profile image"""
        user = request.user
        
        if user.profile_image:
            # Delete the file from storage
            if default_storage.exists(user.profile_image.name):
                default_storage.delete(user.profile_image.name)
            
            # Clear the field
            user.profile_image = None
            user.save()
            
            return Response({'message': 'Profile image deleted successfully'})
        else:
            return Response(
                {'error': 'No profile image to delete'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def retrieve(self, request, pk=None):
        """Get user by ID (admin only)"""
        if not request.user.is_admin_user:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, pk=pk)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def list(self, request):
        """List all users (admin only)"""
        if not request.user.is_admin_user:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        users = User.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)


# Authentication endpoints for dashboard
class FirebaseLoginView(APIView):
    """
    Firebase authentication endpoint for dashboard login
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            id_token = request.data.get('id_token')
            platform = request.data.get('platform', 'web')
            device_id = request.data.get('device_id', '')
            app_version = request.data.get('app_version', '1.0.0')
            
            if not id_token:
                return Response(
                    {'error': 'Firebase ID token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify Firebase token
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
                firebase_uid = decoded_token['uid']
                firebase_email = decoded_token.get('email')
            except Exception as e:
                return Response(
                    {'error': f'Invalid Firebase token: {str(e)}'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get or create user
            user, created = User.objects.get_or_create(
                firebase_uid=firebase_uid,
                defaults={
                    'email': firebase_email,
                    'username': firebase_email,
                    'firebase_email': firebase_email,
                    'user_type': 'customer',
                    'is_active': True,
                }
            )
            
            # Update user data if not created
            if not created:
                if firebase_email and user.email != firebase_email:
                    user.email = firebase_email
                    user.firebase_email = firebase_email
                    user.save()
            
            # Generate JWT token (simplified)
            import time
            access_token = f"access_{user.id}_{int(time.time())}"
            refresh_token = f"refresh_{user.id}_{int(time.time())}"
            session_id = f"session_{user.id}_{int(time.time())}"
            
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type,
                    'is_staff': user.is_staff,
                    'is_admin': user.is_admin_user,
                },
                'access_token': access_token,
                'refresh_token': refresh_token,
                'session_id': session_id,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Authentication failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Additional ViewSets that dashboard might need
class DriverViewSet(viewsets.ModelViewSet):
    """
    ViewSet for driver management (placeholder)
    """
    queryset = User.objects.filter(user_type='driver')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(user_type='driver')


class UserSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user session management (placeholder)
    """
    queryset = User.objects.all()  # Placeholder
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]