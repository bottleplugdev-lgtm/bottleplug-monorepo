from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta
from django.core.paginator import EmptyPage, PageNotAnInteger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import UserSession
from .serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer, UserUpdateSerializer,
    DriverProfileSerializer, UserSessionSerializer, UserStatsSerializer,
    FirebaseAuthSerializer, UserLocationSerializer, DriverAvailabilitySerializer,
    WalletTransactionSerializer
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate
from django.conf import settings
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from .models import User
from .serializers import UserSerializer, UserProfileSerializer
from .permissions import IsOwnerOrReadOnly
from utils.image_utils import validate_image_file, resize_image
from utils.pagination import PreserveStatePagination
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management with Firebase authentication
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = PreserveStatePagination
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserProfileSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter by user type
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Filter by status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by name or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset

    @swagger_auto_schema(
        tags=['auth'],
        operation_description="Verify Firebase ID token and return user data with session creation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase ID token'),
                'platform': openapi.Schema(type=openapi.TYPE_STRING, description='Platform (android/ios)'),
                'device_id': openapi.Schema(type=openapi.TYPE_STRING, description='Device ID'),
                'app_version': openapi.Schema(type=openapi.TYPE_STRING, description='App version')
            },
            required=['id_token']
        )
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Verify Firebase ID token and return user data with session creation"""
        try:
            id_token = request.data.get('id_token')
            if not id_token:
                return Response(
                    {'error': 'ID token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify Firebase ID token
            decoded_token = firebase_auth.verify_id_token(id_token)
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            
            # Get or create user
            user, created = self._get_or_create_user(decoded_token)
            
            # Create or update session
            session = self._create_or_update_session(user, id_token, request)
            
            # Generate JWT token for backend API
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserDetailSerializer(user).data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'session_id': session.id,
                'is_new_user': created,
                'message': 'Authentication successful'
            }, status=status.HTTP_200_OK)

        except firebase_auth.InvalidIdTokenError:
            return Response(
                {'error': 'Invalid ID token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except firebase_auth.ExpiredIdTokenError:
            return Response(
                {'error': 'Expired ID token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except firebase_auth.RevokedIdTokenError:
            return Response(
                {'error': 'Revoked ID token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Error verifying Firebase token: {e}")
            return Response(
                {'error': 'Authentication failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_or_create_user(self, decoded_token):
        """Get or create user based on Firebase token"""
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        
        # Try to find user by Firebase UID first
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            # Update user information if needed
            if email and user.email != email:
                user.email = email
            if name:
                first_name, *last_name_parts = name.split(' ', 1)
                user.first_name = first_name
                user.last_name = last_name_parts[0] if last_name_parts else ''
            user.save()
            return user, False
        except User.DoesNotExist:
            pass
        
        # Try to find user by email if available
        if email:
            try:
                user = User.objects.get(email=email)
                # Link Firebase UID to existing user
                user.firebase_uid = firebase_uid
                if name:
                    first_name, *last_name_parts = name.split(' ', 1)
                    user.first_name = first_name
                    user.last_name = last_name_parts[0] if last_name_parts else ''
                user.save()
                return user, False
            except User.DoesNotExist:
                pass
        
        # Create new user
        first_name, *last_name_parts = name.split(' ', 1) if name else ('', '')
        user = User.objects.create(
            firebase_uid=firebase_uid,
            email=email or f"user_{firebase_uid[:8]}@firebase.local",
            username=email or f"user_{firebase_uid[:8]}",
            first_name=first_name,
            last_name=last_name_parts[0] if last_name_parts else '',
            is_verified=True,
            is_active=True
        )
        
        logger.info(f"Created new user: {user.email} (Firebase UID: {firebase_uid})")
        return user, True

    def _create_or_update_session(self, user, id_token, request):
        """Create or update user session"""
        device_info = {
            'platform': request.data.get('platform', ''),
            'device_id': request.data.get('device_id', ''),
            'app_version': request.data.get('app_version', '')
        }
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Deactivate existing sessions for this user
        UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Create new session
        session = UserSession.objects.create(
            user=user,
            session_token=id_token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
            last_activity=timezone.now()
        )
        
        logger.info(f"Created new session for user: {user.email}")
        return session

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user with Firebase authentication"""
        try:
            id_token = request.data.get('id_token')
            if not id_token:
                return Response(
                    {'error': 'ID token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify Firebase ID token
            decoded_token = firebase_auth.verify_id_token(id_token)
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            
            # Check if user already exists
            if User.objects.filter(firebase_uid=firebase_uid).exists():
                return Response(
                    {'error': 'User already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            user, created = self._get_or_create_user(decoded_token)
            
            if not created:
                return Response(
                    {'error': 'User already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate JWT token
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)

        except firebase_auth.InvalidIdTokenError:
            return Response(
                {'error': 'Invalid ID token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return Response(
                {'error': 'Registration failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user (deactivate session)"""
        try:
            # Deactivate all sessions for this user
            UserSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
            return Response({'message': 'Logged out successfully'})
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return Response(
                {'error': 'Logout failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        """Request password reset"""
        try:
            email = request.data.get('email')
            if not email:
                return Response(
                    {'error': 'Email is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user exists
            try:
                user = User.objects.get(email=email)
                # In Firebase auth, password reset is handled by Firebase
                return Response({'message': 'Password reset instructions sent to your email'})
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            logger.error(f"Error requesting password reset: {e}")
            return Response(
                {'error': 'Password reset request failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def check_exists(self, request):
        """Check if user exists"""
        email = request.query_params.get('email')
        firebase_uid = request.query_params.get('firebase_uid')
        
        if email:
            exists = User.objects.filter(email=email).exists()
        elif firebase_uid:
            exists = User.objects.filter(firebase_uid=firebase_uid).exists()
        else:
            return Response(
                {'error': 'Email or Firebase UID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'exists': exists})

    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Update user location"""
        serializer = UserLocationSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.latitude = serializer.validated_data['latitude']
            user.longitude = serializer.validated_data['longitude']
            user.save()
            return Response({'message': 'Location updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverViewSet(viewsets.ModelViewSet):
    """
    ViewSet for driver-specific operations
    """
    queryset = User.objects.filter(user_type='driver')
    serializer_class = DriverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.filter(user_type='driver')
        
        # Filter by availability
        is_available = self.request.query_params.get('is_available', None)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        # Filter by status
        current_status = self.request.query_params.get('current_status', None)
        if current_status:
            queryset = queryset.filter(current_status=current_status)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def update_availability(self, request):
        """Update driver availability and location"""
        serializer = DriverAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.is_available = serializer.validated_data['is_available']
            user.current_status = serializer.validated_data['current_status']
            
            # Update location if provided
            if 'latitude' in serializer.validated_data and 'longitude' in serializer.validated_data:
                user.latitude = serializer.validated_data['latitude']
                user.longitude = serializer.validated_data['longitude']
            
            user.save()
            return Response({'message': 'Availability updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLocationView(APIView):
    """Update user location"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UserLocationSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.latitude = serializer.validated_data['latitude']
            user.longitude = serializer.validated_data['longitude']
            user.save()
            return Response({'message': 'Location updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletView(APIView):
    """Handle wallet operations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get wallet balance"""
        return Response({
            'balance': request.user.wallet_balance,
            'currency': 'UGX'
        })
    
    def post(self, request):
        """Process wallet transaction"""
        serializer = WalletTransactionSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            amount = serializer.validated_data['amount']
            transaction_type = serializer.validated_data['transaction_type']
            
            if transaction_type == 'debit' and user.wallet_balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            if transaction_type == 'debit':
                user.wallet_balance -= amount
            else:
                user.wallet_balance += amount
            
            user.save()
            
            return Response({
                'message': 'Transaction processed successfully',
                'new_balance': user.wallet_balance
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user sessions (read-only)"""
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserSession.objects.none()
        return UserSession.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a session"""
        try:
            session = self.get_object()
            session.is_active = False
            session.save()
            return Response({'message': 'Session deactivated'})
        except UserSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def deactivate_all(self, request):
        """Deactivate all user sessions"""
        UserSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        return Response({'message': 'All sessions deactivated'})
