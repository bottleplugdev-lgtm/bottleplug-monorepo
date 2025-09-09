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
from payments.models import PaymentTransaction
import hashlib
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
        operation_description="Login with email/password for testing",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password')
            },
            required=['email', 'password']
        )
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='test-login')
    def test_login(self, request):
        """Login with email/password for testing purposes"""
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                # Generate JWT token for backend API
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'user': UserDetailSerializer(user).data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'message': 'Authentication successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error during test login: {e}")
            return Response(
                {'error': 'Authentication failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
            except Exception as e:
                logger.error(f"Firebase token verification failed: {e}")
                # Instead of failing immediately, let's try once more after a short delay
                import time
                time.sleep(0.5)
                try:
                    decoded_token = firebase_auth.verify_id_token(id_token)
                    logger.info("Firebase token verification successful on retry")
                except Exception as retry_error:
                    logger.error(f"Firebase token verification failed on retry: {retry_error}")
                    raise retry_error
                    
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            
            logger.info(f"Successfully decoded Firebase token for user: {email} (UID: {firebase_uid})")
            
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
            import traceback
            error_details = str(e)
            logger.error(f"Error verifying Firebase token: {error_details}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Authentication failed: {error_details}'}, 
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
        
        # Ensure we store a bounded token value (hash) to avoid DB length issues
        session_token_hash = hashlib.sha256((id_token or '').encode('utf-8')).hexdigest()
        
        # If a session already exists with the same token (Firebase id_token), reuse it
        existing_session = UserSession.objects.filter(session_token=session_token_hash).first()
        if existing_session:
            existing_session.user = user
            existing_session.device_info = device_info
            existing_session.ip_address = ip_address
            existing_session.user_agent = user_agent
            existing_session.is_active = True
            existing_session.last_activity = timezone.now()
            existing_session.save()
            logger.info(f"Reused existing session for user: {user.email}")
            return existing_session

        # Deactivate other active sessions for this user
        UserSession.objects.filter(user=user, is_active=True).exclude(session_token=session_token_hash).update(is_active=False)
        
        # Create new session
        session = UserSession.objects.create(
            user=user,
            session_token=session_token_hash,
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

    # SETTINGS ENDPOINTS
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='profile')
    def get_profile(self, request):
        """Return the authenticated user's profile details"""
        return Response(UserDetailSerializer(request.user).data)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='update_profile')
    def update_profile(self, request):
        """Update basic profile fields for the authenticated user"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='preferences')
    def get_preferences(self, request):
        """Return stored user preferences (persisted in saved_addresses JSON)"""
        preferences = {}
        try:
            # saved_addresses can hold any JSON. Use dict with 'preferences' key
            saved = request.user.saved_addresses or {}
            if isinstance(saved, list):
                # migrate: if list, wrap into dict
                saved = { 'addresses': saved }
            preferences = saved.get('preferences', {})
        except Exception:
            preferences = {}
        return Response({ 'preferences': preferences })

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='update_preferences')
    def update_preferences(self, request):
        """Persist user display and notification preferences into saved_addresses JSON"""
        prefs = request.data or {}
        saved = request.user.saved_addresses or {}
        if isinstance(saved, list):
            saved = { 'addresses': saved }
        saved['preferences'] = prefs
        request.user.saved_addresses = saved
        request.user.save(update_fields=['saved_addresses'])
        return Response({ 'preferences': prefs })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='business')
    def get_business(self, request):
        saved = request.user.saved_addresses or {}
        if isinstance(saved, list):
            saved = { 'addresses': saved }
        business = saved.get('business', {})
        return Response({ 'business': business })

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='update_business')
    def update_business(self, request):
        business = request.data or {}
        saved = request.user.saved_addresses or {}
        if isinstance(saved, list):
            saved = { 'addresses': saved }
        saved['business'] = business
        request.user.saved_addresses = saved
        # Also mirror address/phone if provided
        address = business.get('address')
        phone = business.get('phone') or business.get('phone_number')
        update_fields = ['saved_addresses']
        if address is not None:
            request.user.address = address
            update_fields.append('address')
        if phone is not None:
            request.user.phone_number = phone
            update_fields.append('phone_number')
        request.user.save(update_fields=update_fields)
        return Response({ 'business': business })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='change_password')
    def change_password(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'new_password is required'}, status=400)
        user = request.user
        # If user has a usable password, verify current
        if user.has_usable_password():
            if not current_password or not user.check_password(current_password):
                return Response({'error': 'Current password is incorrect'}, status=400)
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'message': 'Password changed successfully'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='sessions')
    def list_sessions(self, request):
        sessions = UserSession.objects.filter(user=request.user).order_by('-last_activity')
        data = UserSessionSerializer(sessions, many=True).data
        return Response({'results': data})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='revoke_session')
    def revoke_session(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'session_id is required'}, status=400)
        try:
            session = UserSession.objects.get(id=session_id, user=request.user)
            session.is_active = False
            session.save(update_fields=['is_active'])
            return Response({'message': 'Session revoked'})
        except UserSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='revoke_all_sessions')
    def revoke_all_sessions(self, request):
        """Deactivate all active sessions for the authenticated user.
        Optionally preserve a session by id: pass preserve_session_id in body.
        """
        preserve_session_id = request.data.get('preserve_session_id')
        qs = UserSession.objects.filter(user=request.user, is_active=True)
        if preserve_session_id:
            qs = qs.exclude(id=preserve_session_id)
        updated = qs.update(is_active=False)
        return Response({'message': 'Sessions revoked', 'revoked_count': updated})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='billing')
    def billing_info(self, request):
        """Return lightweight billing info and history derived from payment transactions"""
        txns = PaymentTransaction.objects.filter(customer_email=request.user.email).order_by('-created_at')[:20]
        history = []
        for t in txns:
            history.append({
                'id': t.id,
                'description': f"{t.payment_type or 'payment'} {t.transaction_id or ''}".strip(),
                'date': getattr(t, 'created_at', None),
                'amount': str(t.amount),
                'currency': t.currency,
                'status': t.status,
            })
        current_plan = {'plan_name': 'Free', 'plan_description': 'Free tier'}
        return Response({'billing_history': history, 'current_plan': current_plan})

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


# Admin login function (outside the ViewSet)
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Admin login endpoint for dashboard users"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check password
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Allow any authenticated user to access dashboard (development mode)
        # if not (user.is_staff or user.is_admin or user.is_superuser):
        #     return Response(
        #         {'error': 'Access denied. Admin privileges required.'}, 
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        
        # Create session
        device_info = {
            'platform': request.data.get('platform', 'web'),
            'device_id': request.data.get('device_id', ''),
            'app_version': request.data.get('app_version', '1.0.0')
        }
        
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if ip_address:
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Deactivate existing sessions
        UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Create new session
        session = UserSession.objects.create(
            user=user,
            session_token=f"admin_session_{user.id}_{timezone.now().timestamp()}",
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
            last_activity=timezone.now()
        )
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"Admin login successful for user: {user.email}")
        
        return Response({
            'user': UserDetailSerializer(user).data,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'session_id': session.id,
            'is_new_user': False,
            'message': 'Admin authentication successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        return Response(
            {'error': 'Authentication failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_firebase_user(request):
    """Create Firebase user for existing backend user"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists in backend
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found in backend'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user already has Firebase UID
        if user.firebase_uid:
            return Response(
                {'error': 'User already has Firebase account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Firebase user using Firebase Admin SDK
        try:
            firebase_user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=f"{user.first_name} {user.last_name}".strip() or user.email,
                email_verified=user.is_verified
            )
            
            # Update backend user with Firebase UID
            user.firebase_uid = firebase_user.uid
            user.save()
            
            logger.info(f"Firebase user created for: {user.email} (UID: {firebase_user.uid})")
            
            return Response({
                'message': 'Firebase user created successfully',
                'firebase_uid': firebase_user.uid,
                'email': email
            }, status=status.HTTP_201_CREATED)
            
        except firebase_auth.EmailAlreadyExistsError:
            return Response(
                {'error': 'Firebase user with this email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as firebase_error:
            logger.error(f"Firebase user creation error: {firebase_error}")
            return Response(
                {'error': 'Failed to create Firebase user'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Create Firebase user error: {e}")
        return Response(
            {'error': 'Firebase user creation failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def firebase_debug(request):
    """Debug Firebase initialization"""
    try:
        import os
        from firebase_admin import _apps
        
        service_account_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'firebase', 'booze-nation-94e3f-firebase-adminsdk-gegcg-c4b6679745.json')
        file_exists = os.path.exists(service_account_path)
        firebase_initialized = len(_apps) > 0
        
        debug_info = {
            'service_account_file_exists': file_exists,
            'firebase_initialized': firebase_initialized,
            'firebase_apps_count': len(_apps),
            'service_account_path': service_account_path
        }
        
        # Test token verification with a dummy token
        try:
            firebase_auth.verify_id_token('dummy_token')
            debug_info['firebase_auth_working'] = True
        except Exception as e:
            debug_info['firebase_auth_working'] = False
            debug_info['firebase_auth_error'] = str(e)
        
        return Response(debug_info)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def migrate_all_users_to_firebase(request):
    """Migrate all existing backend users to Firebase (admin only)"""
    try:
        admin_email = request.data.get('admin_email')
        admin_password = request.data.get('admin_password')
        
        if not admin_email or not admin_password:
            return Response(
                {'error': 'Admin credentials required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify admin credentials
        try:
            admin_user = User.objects.get(email=admin_email, is_superuser=True)
            if not admin_user.check_password(admin_password):
                raise User.DoesNotExist()
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid admin credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get all users without Firebase UID
        users_to_migrate = User.objects.filter(firebase_uid__isnull=True)
        migration_results = {
            'total_users': users_to_migrate.count(),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for user in users_to_migrate:
            try:
                # Create Firebase user with a default password (they'll need to reset)
                temp_password = f"TempPass123_{user.id}"
                
                firebase_user = firebase_auth.create_user(
                    email=user.email,
                    password=temp_password,
                    display_name=f"{user.first_name} {user.last_name}".strip() or user.email,
                    email_verified=user.is_verified
                )
                
                # Update backend user
                user.firebase_uid = firebase_user.uid
                user.save()
                
                migration_results['successful'] += 1
                logger.info(f"Migrated user: {user.email} (UID: {firebase_user.uid})")
                
            except firebase_auth.EmailAlreadyExistsError:
                migration_results['errors'].append(f"{user.email}: Firebase user already exists")
                migration_results['failed'] += 1
            except Exception as e:
                migration_results['errors'].append(f"{user.email}: {str(e)}")
                migration_results['failed'] += 1
        
        return Response({
            'message': 'Migration completed',
            'results': migration_results
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return Response(
            {'error': 'Migration failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
