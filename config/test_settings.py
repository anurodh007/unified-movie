"""
test_settings.py

Inherits everything from config.settings and replaces:
    - DATABASE -> SQLite in-memory
    - CACHES -> LocMemCache (no Redis)
    - PASSWORD_HASHERS -> faster MD5 hasher
    - Disables django-silk profiling middleware
    - Disables drf-spectacular schema generation overhead
"""

from config.settings import *
import tempfile

# Use test-specific URL configuration
ROOT_URLCONF = 'config.test_urls'


# Use SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


# Use local memory cache instead of redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}


# Faster password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


# Temp dir for media
MEDIA_ROOT = tempfile.mkdtemp()


# Remove silk profiling middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'silk' not in m]

# Remove silk from installed apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'silk']


# Ensure DEBUG is True
DEBUG = True


# JWT - leep tokens short-lived
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'UPDATE_LAST_LOGIN': False,
}


# Silence logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {'null': {'class': 'logging.NullHandler'}},
    'root': {'handlers': ['null']},
}