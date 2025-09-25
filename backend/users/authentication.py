import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from decouple import config
import os

User = get_user_model()


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for Firebase
    """
    
    def authenticate(self, request):
        # Get the Firebase token from the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        platform = request.META.get('HTTP_X_PLATFORM', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        app_version = request.META.get('HTTP_X_APP_VERSION', 'unknown')
        
        # Enhanced debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[{platform.upper()}] Firebase auth attempt - Header: {auth_header[:50]}... User-Agent: {user_agent[:100]}... App-Version: {app_version}")
        
        if not auth_header.startswith('Bearer '):
            logger.warning(f"[{platform.upper()}] No Bearer token found in Authorization header")
            return None
        
        token = auth_header.split('Bearer ')[1]
        
        if not token:
            logger.warning(f"[{platform.upper()}] Empty token after Bearer prefix")
            return None
        
        # Validate token format (Firebase tokens are JWT tokens that start with 'eyJ')
        if not token.startswith('eyJ'):
            logger.warning(f"[{platform.upper()}] Invalid token format - doesn't start with 'eyJ'. Token: {token[:20]}...")
            return None
        
        logger.info(f"[{platform.upper()}] Token format valid - Length: {len(token)}, Starts with: {token[:20]}...")
        
        try:
            # Firebase should already be initialized in settings.py
            # No need to re-initialize here
            
            # Verify the Firebase token
            logger.info(f"[{platform.upper()}] Attempting Firebase token verification...")
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token['uid']
            firebase_email = decoded_token.get('email', '')
            is_anonymous = decoded_token.get('firebase', {}).get('sign_in_provider') == 'anonymous'
            
            logger.info(f"[{platform.upper()}] Token verified successfully - UID: {firebase_uid}, Email: {firebase_email}, Anonymous: {is_anonymous}")
            
            # Get or create user
            logger.info(f"[{platform.upper()}] Attempting user lookup/creation...")
            user, created = self._get_or_create_user(decoded_token)
            
            logger.info(f"[{platform.upper()}] User {'created' if created else 'found'}: {user.username} (ID: {user.id}, Type: {getattr(user, 'user_type', 'unknown')})")
            
            return (user, None)
            
        except Exception as e:
            # Enhanced error logging with specific error types
            logger.error(f"[{platform.upper()}] Firebase authentication failed - Error: {str(e)}")
            logger.error(f"[{platform.upper()}] Error type: {type(e).__name__}")
            
            # Log specific Firebase errors
            if hasattr(e, 'code'):
                logger.error(f"[{platform.upper()}] Firebase error code: {e.code}")
            
            # Don't raise an exception - let other authentication classes try
            # This prevents Firebase auth from blocking JWT auth
            return None
    
    def _get_or_create_user(self, decoded_token):
        """
        Get or create a user based on Firebase token
        """
        firebase_uid = decoded_token['uid']
        firebase_email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        picture = decoded_token.get('picture', '')
        
        # Try to find user by Firebase UID first
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            # Update user information
            if firebase_email and user.email != firebase_email:
                user.email = firebase_email
            if name:
                first_name, *last_name_parts = name.split(' ', 1)
                user.first_name = first_name
                user.last_name = last_name_parts[0] if last_name_parts else ''
            if picture:
                user.profile_image = picture
            user.save()
            return user, False
        except User.DoesNotExist:
            pass
        
        # Try to find user by email (only for non-anonymous users)
        if firebase_email:
            try:
                user = User.objects.get(email=firebase_email)
                # Link Firebase UID to existing user
                user.firebase_uid = firebase_uid
                if picture:
                    user.profile_image = picture
                user.save()
                return user, False
            except User.DoesNotExist:
                pass
        
        # Create new user
        first_name, *last_name_parts = name.split(' ', 1) if name else ('', '')
        
        # Handle anonymous users (no email)
        if not firebase_email:
            # For anonymous users, create a username from UID
            username = f"anonymous_{firebase_uid[:8]}"
            email = f"{username}@anonymous.bottleplug.com"
        else:
            username = firebase_email
            email = firebase_email
        
        user = User.objects.create(
            firebase_uid=firebase_uid,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name_parts[0] if last_name_parts else '',
            profile_image=picture,
            is_verified=True,  # Firebase users are verified
        )
        
        return user, True 