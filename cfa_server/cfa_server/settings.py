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
from datetime import timedelta

import firebase_admin
from firebase_admin import credentials
from firebase_admin import initialize_app

ENVIRONMENT = os.environ.get("mode", "PRODUCTION")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-0mfz%)780(7i=w)p8w^n$s7j#(u!bq$1zd(m!@19sa5$9wb^gw"

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = ENVIRONMENT == "DEVELOPMENT"
DEBUG = False
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
   ## "rest_framework.authtoken", ## enabline tis nabame
    "drf_spectacular",
    "django_filters",
    "debug_toolbar",
    "crispy_forms",
    "crispy_bootstrap5",
    "ckeditor",
    "ckeditor_uploader",
    "fcm_django",
    "corsheaders",
    "axes",
    "django_password_validators",
    "django_password_validators.password_history",
    "captcha",
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
    "axes.middleware.AxesMiddleware",
    "api.middleware.OneSessionPerUserMiddleware",  # One session
    "api.middleware.DisableOptionsMiddleware",  # Disable options
    "api.middleware.HSTSMiddleware",
    "api.middleware.RSAMiddleware",
    "api.middleware.CustomCSPMiddleware",
   # "debug_toolbar.middlewar.DebugToolbarMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = "cfa_server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "api/templates"),
            os.path.join(BASE_DIR, "templates"), # Add this line if you have project-level templates
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "csp.context_processors.nonce",
            ],
        },
    },
]

WSGI_APPLICATION = "cfa_server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
"""
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("DB_NAME", "cfa"),
        "USER": os.environ.get("DB_USER", "hello"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", 5432),
    }
}
"""
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "cdb",
        "USER": "cuser",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
# STATIC_ROOT = 'portal/static/'
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "mobile_reset_password_otp": "5/day",
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 9,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "django_password_validators.password_history.password_validation.UniquePasswordsValidator",
        "OPTIONS": {
            # How many recently entered passwords matter.
            # Passwords out of range are deleted.
            # Default: 0 - All passwords entered by the user. All password hashes are stored.
            "last_passwords": 5  # Only the last 5 passwords entered by the user
        },
    },
    {
        "NAME": "django_password_validators.password_character_requirements.password_validation.PasswordCharacterValidator",
        "OPTIONS": {
            "min_length_digit": 1,
            "min_length_alpha": 1,
            "min_length_special": 1,
            "min_length_lower": 1,
            "min_length_upper": 1,
            "special_characters": "~!@#$%^&*()_+{}\":;'[]",
        },
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
    "axes.backends.AxesBackend",  # Axes must be first
    # "api.utils.CustomBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# start logg
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
# end log 
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
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} : {asctime} : {module} : {filename}: {funcName} : {lineno} :  {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './api.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'level': 'DEBUG',
           # 'propagate': True,
        },
    },
}
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


cred = credentials.Certificate(str(BASE_DIR) + "/credentials.json")
firebase_admin.initialize_app(cred, {'projectId':'drug-b3460'})

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
    "https://apcrime.arunachal.gov.in",
    "http://10.0.104.12:9005",
]

CSRF_TRUSTED_ORIGINS = [
    "https://apcrime.arunachal.gov.in",
#    "http://10.0.104.12:9005",
    "http://localhost"
]


CSRF_COOKIE_SECURE = ENVIRONMENT != "DEVELOPMENT"

SESSION_COOKIE_HTTPONLY = ENVIRONMENT != "DEVELOPMENT"
SESSION_COOKIE_SECURE = ENVIRONMENT != "DEVELOPMENT"
SESSION_COOKIE_SAMESITE = "Strict"  # or 'Lax'
# SESSION_COOKIE_DOMAIN="printing.merrygold.xyz"

SESSION_COOKIE_AGE = 1800
SESSION_EXPIRE_SECONDS = 1200  # 10 mins
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 10  # 10 mins
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 2
AXES_RESET_ON_SUCCESS = True
AXES_DISABLE_ACCESS_LOG = True # new added 
AXES_NEVER_LOCKOUT_WHITELIST = True # new added 

CSRF_COOKIE_SECURE = ENVIRONMENT != "DEVELOPMENT"

CSP_DEFAULT_SRC = "'self'"
CSP_SCRIPT_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/js/bootstrap.bundle.min.js",
)
CSP_IMG_SRC = ("'self'",)
CSP_SCRIPT_HASHES = (
    "'sha384-oBqDVmMz9ATKxIep9tiCxS/Z9fNfEXiDAYTujMAeBAsjFuCZSmKbSSUnQlmh/jp3'",
)
CSP_FONT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'nonce'", "www.google.com")
CSP_OBJECT_SRC = "'none'"
CSP_STYLE_SRC_ELEM = ("'self'", "www.google.com")
CSP_INCLUDE_NONCE_IN = ("script-src", "style-src-elem", "img-src data", "style-src")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

GOOGLE_MAP_API_KEY = "AIzaSyDM7gudJWf-zdilGmh_cmcI4otu_cJh8Aw"

OTP_VALIDITY_TIME: int = 5 * 60


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=30),
    "TOKEN_OBTAIN_SERIALIZER": "api.serializers.CustomTokenObtainSerializer",
    "ROTATE_REFRESH_TOKENS": True,
}
