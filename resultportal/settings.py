import os
import sys
from pathlib import Path
from datetime import timedelta
from result_portal_lib.models import configure_models

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.parent))

SECRET_KEY = 'django-insecure-your-secret-key-here'
DEBUG = False
ALLOWED_HOSTS = ["0536cc201ee8495b89348bd8012ba2dd.vfs.cloud9.us-east-1.amazonaws.com", "172.31.5.186", "ec2-44-199-250-137.compute-1.amazonaws.com", "localhost",]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resultportal.urls'
WSGI_APPLICATION = 'resultportal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/ec2-user/environment/resultportal/db.sqlite3',
    }
    
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True 

AUTHENTICATION_BACKENDS = ['result_portal_lib.auth.DynamoDBAuthBackend']

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'USER_ID_FIELD': 'username',  # Match your hash_key
    'USER_ID_CLAIM': 'user_id',
}

CORS_ALLOW_ALL_ORIGINS = True


# AWS CREDENTIALS
AWS_REGION = 'us-east-1'
configure_models(AWS_REGION)
S3_BUCKET_NAME = 'result-portal-bucket'
SNS_TOPIC_NAME = 'teachernotifications'
DYNAMODB_TABLES = {
    'Users': {'read_capacity': 5, 'write_capacity': 5},
    'Results': {'read_capacity': 5, 'write_capacity': 5},
    'Complaints': {'read_capacity': 5, 'write_capacity': 5}
}
PROGRAMMATIC_AWS_SETUP = True  # Set to False if credentials fail

SES_SENDER = 'animashaunadams@gmail.com'

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