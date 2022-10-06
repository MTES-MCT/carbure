"""
Django settings for carbure project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from django_query_profiler.settings import *

import environ
env = environ.Env(
    DEBUG=(bool, False),
    TEST=(bool, False),
    IMAGE_TAG=(str, "local"),
    CARBURE_HOME=(str, ""),
    ALLOWED_HOSTS=(list, ["localhost"]),
    CSRF_TRUSTED_ORIGINS=(list, ["http://localhost:8000"]),
    DJANGO_QUERY_PROFILER_REDIS_HOST=(str, "localhost"),
    DATABASE_URL=(str, ""),
    REDIS_URL=(str, ""),
    SENTRY_DSN=(str, ""),
    AWS_ACCESS_KEY_ID=(str, ""),
    AWS_SECRET_ACCESS_KEY=(str, ""),
    AWS_S3_ENDPOINT_URL=(str, ""),
    AWS_S3_REGION_NAME=(str, ""),
    AWS_S3_USE_SSL=(str, ""),
    AWS_STORAGE_BUCKET_NAME=(str, ""),
    AWS_DCDOCS_STORAGE_BUCKET_NAME=(str, ""),
    EMAIL_HOST=(str, ""),
    EMAIL_PORT=(str, ""),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(str, ""),
)

# False if not in os.environ
DEBUG = env('DEBUG')
# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures'),)

if env('TEST') is False:
    sentry_sdk.init(
        dsn=env('SENTRY_DSN'),
        integrations=[DjangoIntegration()],

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

SESSION_COOKIE_AGE = 60*60*24*30 # 30 days
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SECURE=env('IMAGE_TAG') in ('dev', 'staging', 'prod')

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE=env('IMAGE_TAG') in ('dev', 'staging', 'prod')

OTP_EMAIL_TOKEN_VALIDITY = 1800 # 30 minutes
OTP_EMAIL_THROTTLE_FACTOR = 0 # no throttle

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_email',
    'django_admin_listfilter_dropdown',
    'authtools',
    'huey.contrib.djhuey',
    'core',
    'producers',
    'certificates',
    'api',
    'doublecount',
    'ml',
]

AUTH_USER_MODEL = 'authtools.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'spa.middleware.SPAMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.logging_middleware.LoggingMiddleware',
]

ROOT_URLCONF = 'carbure.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [env('CARBURE_HOME') + '/web/templates'],
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

WSGI_APPLICATION = 'carbure.wsgi.application'

# new in django 3.2, define default type for 'id' primary key
# can also be done in each model with
# id = models.AutoField(primary_key=True)
DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# Load db setup from DATABASE_URL env variable
DATABASES = {"default": env.db()}

if env('TEST') == 1:
    print("DB TESTING MODE")
    DATABASES['default']['OPTIONS'] = {
        'auth_plugin': 'mysql_native_password'
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/assets/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = "spa.storage.SPAStaticFilesStorage"

WHITENOISE_ALLOW_ALL_ORIGINS=False

if env('IMAGE_TAG') in ['dev', 'staging', 'prod']:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, '../front/build')]


DEFAULT_FROM_EMAIL = "noreply@carbure.beta.gouv.fr"
if env('IMAGE_TAG') in ['dev', 'staging', 'prod']:
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env('EMAIL_PORT')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = env('EMAIL_USE_TLS')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# file storage
DEFAULT_FILE_STORAGE = 'carbure.storage_backends.MediaStorage'
AWS_DCDOCS_STORAGE_BUCKET_NAME = env('AWS_DCDOCS_STORAGE_BUCKET_NAME')
if env('TEST') is False:
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
    AWS_S3_USE_SSL = 1
    AWS_DEFAULT_ACL = None
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_VERIFY = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # change debug level as appropiate
            'propagate': False,
        },
    },
}

# Huey settings
HUEY = {
    'name': 'carbure',
    'huey_class': 'huey.RedisHuey',
    'url': env('REDIS_URL'),
    'immediate': False,
    'consumer': {'workers': 2}
}


if DEBUG:
    INSTALLED_APPS += ['django_query_profiler']
    DATABASES["default"]["ENGINE"] = "django_query_profiler." + DATABASES["default"]["ENGINE"]
    MIDDLEWARE = ['django_query_profiler.client.middleware.QueryProfilerMiddleware'] + MIDDLEWARE


# CSP header configuration
CSP_DEFAULT_SRC=("'self'", "stats.data.gouv.fr", "metabase.carbure.beta.gouv.fr")
