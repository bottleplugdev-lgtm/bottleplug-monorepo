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

    @swagger_auto_schema(
        tags=['users'],
        operation_description="Get current user's profile"
    )
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['users'],
        operation_description="Update current user's profile",
        request_body=UserProfileUpdateSerializer
    )
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

    @swagger_auto_schema(
        tags=['users'],
        operation_description="Upload profile image"
    )
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

    @swagger_auto_schema(
        tags=['users'],
        operation_description="Delete profile image"
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

    @swagger_auto_schema(
        tags=['users'],
        operation_description="Get user by ID (admin only)"
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

    @swagger_auto_schema(
        tags=['users'],
        operation_description="List all users (admin only)"
    )
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