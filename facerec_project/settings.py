import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-pon_aqui_uno_secreto'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # CORS
    'corsheaders',

    # Apps de terceros
    'rest_framework',
    'rest_framework_simplejwt',

    # Tu app local
    'accounts',
]

MIDDLEWARE = [
    # CORS
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'facerec_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # si tuvieras plantillas, las pones aquí
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

WSGI_APPLICATION = 'facerec_project.wsgi.application'

# Configuración de PostgreSQL (ajusta con tus credenciales)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'facer',       #facerecdb
        'USER': 'postgres',        
        'PASSWORD': '12341234',  
        'HOST': 'localhost',       
        'PORT': '5432',            
    }
}

# Indicar que usamos un CustomUser
AUTH_USER_MODEL = 'accounts.CustomUser'

# Config de DRF + JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Configurar CORS
CORS_ALLOW_ALL_ORIGINS = True
# O si prefieres restringir: 
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173"
# ]

# Archivos estáticos y media
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
