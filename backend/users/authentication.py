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
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split('Bearer ')[1]
        
        if not token:
            return None
        
        # Skip JWT tokens - let JWTAuthentication handle them
        # Firebase tokens typically don't start with 'eyJ' (JWT format)
        # and are much longer than typical JWTs
        if token.startswith('eyJ') and len(token) < 500:
            # This looks like a JWT token, not a Firebase token
            return None
        
        try:
            # Firebase should already be initialized in settings.py
            # No need to re-initialize here
            
            # Verify the Firebase token
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token['uid']
            firebase_email = decoded_token.get('email', '')
            
            # Get or create user
            user, created = self._get_or_create_user(decoded_token)
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Firebase authentication successful for user: {user.username} (type: {user.user_type})")
            
            return (user, None)
            
        except Exception as e:
            # Don't raise an exception - let other authentication classes try
            # This prevents Firebase auth from blocking JWT auth
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Firebase authentication failed: {str(e)}")
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