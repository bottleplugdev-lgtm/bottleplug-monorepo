import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from decouple import config
import os
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class MobileFirebaseAuthentication(authentication.BaseAuthentication):
    """
    Mobile-optimized Firebase authentication with enhanced error handling and logging.
    This class is specifically designed for mobile applications (iOS/Android) and
    provides better debugging and error handling for mobile-specific scenarios.
    """
    
    def authenticate(self, request):
        # Get the Firebase token from the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        platform = request.META.get('HTTP_X_PLATFORM', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        app_version = request.META.get('HTTP_X_APP_VERSION', 'unknown')
        device_id = request.META.get('HTTP_X_DEVICE_ID', 'unknown')
        
        # Enhanced mobile-specific debug logging
        logger.info(f"[MOBILE-{platform.upper()}] Auth attempt - App: {app_version}, Device: {device_id}")
        logger.info(f"[MOBILE-{platform.upper()}] User-Agent: {user_agent[:150]}...")
        logger.info(f"[MOBILE-{platform.upper()}] Auth header present: {bool(auth_header)}")
        
        if not auth_header:
            logger.warning(f"[MOBILE-{platform.upper()}] No Authorization header found")
            return None
        
        if not auth_header.startswith('Bearer '):
            logger.warning(f"[MOBILE-{platform.upper()}] Authorization header doesn't start with 'Bearer'")
            return None
        
        token = auth_header.split('Bearer ')[1]
        
        if not token:
            logger.warning(f"[MOBILE-{platform.upper()}] Empty token after Bearer prefix")
            return None
        
        # Validate token format (Firebase tokens are JWT tokens that start with 'eyJ')
        if not token.startswith('eyJ'):
            logger.warning(f"[MOBILE-{platform.upper()}] Invalid token format - doesn't start with 'eyJ'. Token: {token[:30]}...")
            return None
        
        logger.info(f"[MOBILE-{platform.upper()}] Token format valid - Length: {len(token)}")
        
        try:
            # Verify the Firebase token with enhanced error handling
            logger.info(f"[MOBILE-{platform.upper()}] Starting Firebase token verification...")
            decoded_token = auth.verify_id_token(token)
            
            firebase_uid = decoded_token['uid']
            firebase_email = decoded_token.get('email', '')
            is_anonymous = decoded_token.get('firebase', {}).get('sign_in_provider') == 'anonymous'
            auth_time = decoded_token.get('auth_time', 0)
            exp_time = decoded_token.get('exp', 0)
            
            logger.info(f"[MOBILE-{platform.upper()}] Token verified - UID: {firebase_uid}")
            logger.info(f"[MOBILE-{platform.upper()}] Email: {firebase_email}, Anonymous: {is_anonymous}")
            logger.info(f"[MOBILE-{platform.upper()}] Auth time: {auth_time}, Exp time: {exp_time}")
            
            # Get or create user with mobile-specific handling
            logger.info(f"[MOBILE-{platform.upper()}] Attempting user lookup/creation...")
            user, created = self._get_or_create_mobile_user(decoded_token, platform, device_id)
            
            if created:
                logger.info(f"[MOBILE-{platform.upper()}] New mobile user created: {user.username} (ID: {user.id})")
            else:
                logger.info(f"[MOBILE-{platform.upper()}] Existing mobile user found: {user.username} (ID: {user.id})")
            
            # Update user's mobile session info
            self._update_mobile_session_info(user, platform, device_id, app_version)
            
            return (user, None)
            
        except auth.InvalidIdTokenError as e:
            logger.error(f"[MOBILE-{platform.upper()}] Invalid Firebase ID token: {str(e)}")
            return None
        except auth.ExpiredIdTokenError as e:
            logger.error(f"[MOBILE-{platform.upper()}] Expired Firebase ID token: {str(e)}")
            return None
        except auth.RevokedIdTokenError as e:
            logger.error(f"[MOBILE-{platform.upper()}] Revoked Firebase ID token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[MOBILE-{platform.upper()}] Firebase authentication error: {str(e)}")
            logger.error(f"[MOBILE-{platform.upper()}] Error type: {type(e).__name__}")
            
            # Log additional context for debugging
            import traceback
            logger.error(f"[MOBILE-{platform.upper()}] Traceback: {traceback.format_exc()}")
            
            return None
    
    def _get_or_create_mobile_user(self, decoded_token, platform, device_id):
        """
        Mobile-optimized user creation with better defaults and error handling
        """
        firebase_uid = decoded_token['uid']
        firebase_email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        picture = decoded_token.get('picture', '')
        
        # Try to find user by Firebase UID first
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            logger.info(f"[MOBILE] User found by Firebase UID: {user.username}")
            
            # Update user information
            updated = False
            if firebase_email and user.email != firebase_email:
                user.email = firebase_email
                user.firebase_email = firebase_email
                updated = True
            
            if name:
                first_name, *last_name_parts = name.split(' ', 1)
                if user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if last_name_parts and user.last_name != last_name_parts[0]:
                    user.last_name = last_name_parts[0]
                    updated = True
            
            if picture and user.profile_image != picture:
                user.profile_image = picture
                updated = True
            
            # Mark as mobile user
            if not hasattr(user, 'is_mobile_user') or not user.is_mobile_user:
                user.is_mobile_user = True
                updated = True
            
            if updated:
                user.save()
                logger.info(f"[MOBILE] User updated: {user.username}")
            
            return user, False
            
        except User.DoesNotExist:
            logger.info(f"[MOBILE] No user found with Firebase UID: {firebase_uid}")
        
        # Try to find user by email (only for non-anonymous users)
        if firebase_email:
            try:
                user = User.objects.get(email=firebase_email)
                logger.info(f"[MOBILE] User found by email: {user.username}")
                
                # Link Firebase UID to existing user
                user.firebase_uid = firebase_uid
                user.firebase_email = firebase_email
                user.is_mobile_user = True
                
                if picture:
                    user.profile_image = picture
                
                user.save()
                return user, False
                
            except User.DoesNotExist:
                logger.info(f"[MOBILE] No user found with email: {firebase_email}")
        
        # Create new mobile user
        logger.info(f"[MOBILE] Creating new mobile user...")
        
        # Handle anonymous users (no email)
        if not firebase_email:
            username = f"mobile_anon_{firebase_uid[:8]}"
            email = f"{username}@mobile.bottleplug.com"
            logger.info(f"[MOBILE] Creating anonymous mobile user: {username}")
        else:
            username = firebase_email
            email = firebase_email
            logger.info(f"[MOBILE] Creating mobile user with email: {email}")
        
        # Parse name
        first_name, *last_name_parts = name.split(' ', 1) if name else ('', '')
        
        try:
            user = User.objects.create(
                firebase_uid=firebase_uid,
                email=email,
                username=username,
                firebase_email=firebase_email,
                first_name=first_name,
                last_name=last_name_parts[0] if last_name_parts else '',
                profile_image=picture,
                is_verified=True,  # Firebase users are verified
                is_mobile_user=True,  # Flag as mobile user
                user_type='customer',  # Default to customer
                is_active=True,
            )
            
            logger.info(f"[MOBILE] New mobile user created successfully: {user.username} (ID: {user.id})")
            return user, True
            
        except Exception as e:
            logger.error(f"[MOBILE] Failed to create new user: {str(e)}")
            raise
    
    def _update_mobile_session_info(self, user, platform, device_id, app_version):
        """
        Update user's mobile session information for analytics and support
        """
        try:
            # Update last login time
            user.last_login = timezone.now()
            
            # Store mobile session info (if you have these fields)
            if hasattr(user, 'last_platform'):
                user.last_platform = platform
            if hasattr(user, 'last_device_id'):
                user.last_device_id = device_id
            if hasattr(user, 'last_app_version'):
                user.last_app_version = app_version
            
            user.save(update_fields=['last_login'])
            
            logger.info(f"[MOBILE] Updated session info for user: {user.username}")
            
        except Exception as e:
            logger.warning(f"[MOBILE] Failed to update session info: {str(e)}")
    
    def authenticate_header(self, request):
        return 'Bearer realm="mobile-api"'
