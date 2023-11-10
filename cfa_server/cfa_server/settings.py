"""
Django settings for cfa_server project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
import logging

import firebase_admin
from firebase_admin import credentials
from firebase_admin import initialize_app

ENVIRONMENT = os.environ.get('mode', 'PRODUCTION')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-0mfz%)780(7i=w)p8w^n$s7j#(u!bq$1zd(m!@19sa5$9wb^gw"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENVIRONMENT == 'DEVELOPMENT'

ALLOWED_HOSTS = ["*"]
TIME_ZONE = "Asia/Kolkata"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "api",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_filters",
    "debug_toolbar",
    "crispy_forms",
    "crispy_bootstrap5",
    "ckeditor",
    "ckeditor_uploader",
    "fcm_django",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = "cfa_server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cfa_server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# STATIC_ROOT = 'portal/static/'
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = "staticfiles/"
STATICFILES_DIRS = (str(BASE_DIR / "static"),)
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "api.cUser"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


""" LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': './django.log',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(level)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(level)s %(asctime)s %(message)s',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'api': {
            'handlers': ['console','file'],
            'level': 'INFO',
        },
        'cfa_server': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

 """
"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': './api.log',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format=': '%(asctime)s %(levelname)s [%(funcName)s:%(lineno)d] %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'api': {
            'handlers': ['console','file'],
            'level': 'INFO',
        },
    },
}
 """

INTERNAL_IPS = ["127.0.0.1"]


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_REDIRECT_URL = "/"

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"

CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_FILENAME_GENERATOR = 'utils.get_filename'

MEDIA_ROOT = str(BASE_DIR / "media")

MEDIA_URL = "/media/"
FCM_DJANGO_SETTINGS = {
    # an instance of firebase_admin.App to be used as default for all fcm-django requests
    # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": None,
    # default: _('FCM Django')
    "APP_VERBOSE_NAME": "CFA Firebase",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": True,
    # "FCM_SERVER_KEY": "AAAAUBWqdfo:APA91bEm3ib6_TlLIJ5YpAU6BjyQ7X9GoXeghkgqiBwNPPkr_FP9NjdhVk8EZqCUvgWUIf2vhk5eUnSkJELy7JtJfv1qOGM_UZtxu0FI3BkpUQMxdX-aO3xdvfTKteAkbAc2vXy1xCXu"
}


cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

SPECTACULAR_SETTINGS = {
    "TITLE": "CFA API",
    "DESCRIPTION": "Documentation of API endpoints of CFA",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
    "SERVE_PERMISSIONS": [],
}

ALLOWED_VIDEO_TYPES = ["audio/mp4", "audio/mpeg"]
ALLOWED_AUDIO_TYPES = ["video/mp3", "video/WebM", "audio/aac"]
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/heic"]
ALLOWED_DOC_TYPES = [
    "application/pdf",
    "application/msword",  # doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
]

ALLOWED_FILE_TYPES = (
    ALLOWED_VIDEO_TYPES + ALLOWED_AUDIO_TYPES + ALLOWED_IMAGE_TYPES + ALLOWED_DOC_TYPES
)

CORS_ALLOWED_ORIGINS = [
    "https://arpreport.merrygold.xyz",
    "http://193.168.195.153:9001",
]

CSRF_TRUSTED_ORIGINS = [
    "https://arpreport.merrygold.xyz",
    "http://193.168.195.153:9001",
]
