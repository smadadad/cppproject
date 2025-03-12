import os
import sys
from pathlib import Path
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.parent))


# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-here')  # Use env var for security
DEBUG = os.environ.get('DEBUG', 'False') == 'True'  # Env-driven, default False
ALLOWED_HOSTS = [
    "0536cc201ee8495b89348bd8012ba2dd.vfs.cloud9.us-east-1.amazonaws.com",
    "172.31.5.186",
    "ec2-44-199-250-137.compute-1.amazonaws.com",
    "localhost",
    # Add API Gateway domain if known, e.g., "*.execute-api.us-east-1.amazonaws.com"
]

# Installed apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'api.apps.ApiConfig',
]



# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    
]

# URL and WSGI config
ROOT_URLCONF = 'resultportal.urls'
WSGI_APPLICATION = 'resultportal.wsgi.application'

# No DATABASES - using DynamoDB only


# Authentication
AUTHENTICATION_BACKENDS = ['api.auth.DynamoDBAuthBackend'] 

FRONTEND_URL = 'https://yourdomain.com'  # Replace with your actual Next.js URL

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = '/static/'

# Templates (minimal, since no Django templates used)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]



# REST Framework with JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}



# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'USER_ID_FIELD': 'username',  # Matches PynamoDB User hash_key
    'USER_ID_CLAIM': 'user_id',
}



# CORS for frontend
CORS_ALLOW_ALL_ORIGINS = True  # Tighten this in prod (e.g., CORS_ALLOWED_ORIGINS)



# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = 'result-portal-bucket'
SNS_TOPIC_NAME = 'arn:aws:sns:us-east-1:your-account-id:ResultPortalEmails'  # Replace with actual ARN
DYNAMODB_TABLES = {
    'Users': {'read_capacity': 5, 'write_capacity': 5},
    'Results': {'read_capacity': 5, 'write_capacity': 5},
    'Complaints': {'read_capacity': 5, 'write_capacity': 5}
}
PROGRAMMATIC_AWS_SETUP = True  # Set to False if manual setup preferred

# Logging
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
        'propagate': True,
    },
}