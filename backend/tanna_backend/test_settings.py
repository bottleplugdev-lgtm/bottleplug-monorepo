# Test settings for CI/CD
from .settings import *
import os

# Override settings for testing
DEBUG = True
SECRET_KEY = 'test-secret-key-for-github-actions'

# Use PostgreSQL for tests (same as production)
# Database configuration will come from environment variables
# This ensures we test with the same database type as production

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable Firebase for tests
FIREBASE_CREDENTIALS_PATH = None
FIREBASE_PRIVATE_KEY = None
FIREBASE_CLIENT_EMAIL = None
FIREBASE_PROJECT_ID = None

# Disable Celery for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable email sending during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Use dummy cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable password validation for tests
AUTH_PASSWORD_VALIDATORS = []

# Use simple password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable static file collection during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Test media settings
MEDIA_ROOT = '/tmp/test_media'
MEDIA_URL = '/test_media/'

# Disable CORS checks for tests
CORS_ALLOW_ALL_ORIGINS = True

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
