"""
Django settings for BrainDump project.

Level 5 Diploma - Unit 3: Back End Development
Author: Brandon
Date: 2024

This settings file is configured for both development and production environments.
It uses environment variables for sensitive data and includes security best practices.
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url

# =============================================================================
# CORE SETTINGS
# =============================================================================

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security: Secret key stored in environment variable
SECRET_KEY = config('SECRET_KEY')

# Debug mode: False in production, True in development
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts: Configured via environment variable
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Check if we're in production environment (not just DEBUG=False for local testing)
IS_PRODUCTION = config('IS_PRODUCTION', default=False, cast=bool)


# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom apps
    'posts',  # Main application for posts, comments, and voting
    'tailwind',  # Tailwind CSS integration
    'theme',     # Tailwind theme app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'braindump.urls'


# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Project-level templates
        'APP_DIRS': True,  # Enable app-level templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'braindump.wsgi.application'


# =============================================================================
# DATABASE
# =============================================================================

# Database configuration using dj-database-url
# Supports both SQLite (development) and PostgreSQL (production/Heroku)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
    )
}


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic will place files

# Additional directories to look for static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Storage configuration for static files
# Use ManifestStaticFilesStorage in development/testing to allow missing files
# Switch to CompressedManifestStaticFilesStorage in production
if DEBUG or not IS_PRODUCTION:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            # Use regular static files storage when not in production
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            # Use Whitenoise for production static file serving with compression
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }


# =============================================================================
# AUTHENTICATION
# =============================================================================

# Redirect URLs after login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'


# =============================================================================
# TAILWIND CSS CONFIGURATION (Development Only)
# =============================================================================

if DEBUG:
    TAILWIND_APP_NAME = 'theme'  # Name of the Tailwind theme app
    INTERNAL_IPS = ['127.0.0.1']  # Required for Tailwind hot reload in development


# =============================================================================
# SECURITY SETTINGS (Production Only)
# =============================================================================

if not DEBUG and IS_PRODUCTION:
    # HTTPS/SSL Settings
    SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
    SESSION_COOKIE_SECURE = True  # Send session cookie only over HTTPS
    CSRF_COOKIE_SECURE = True  # Send CSRF cookie only over HTTPS

    # HTTP Strict Transport Security (HSTS)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Additional Security Headers
    SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filter
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
    X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking


# =============================================================================
# DEFAULT FIELD TYPE
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# LOGGING CONFIGURATION (for debugging when DEBUG=False)
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
