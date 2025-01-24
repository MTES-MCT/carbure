"""
Django settings for carbure project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env(
    DEBUG=(bool, False),
    TEST=(bool, False),
    IMAGE_TAG=(str, "local"),
    CARBURE_HOME=(str, ""),
    ALLOWED_HOSTS=(list, ["localhost"]),
    CSRF_TRUSTED_ORIGINS=(list, ["http://localhost:8000"]),
    DATABASE_URL=(str, ""),
    REDIS_URL=(str, ""),
    SENTRY_DSN=(str, ""),
    AWS_ACCESS_KEY_ID=(str, ""),
    AWS_SECRET_ACCESS_KEY=(str, ""),
    AWS_S3_ENDPOINT_URL=(str, ""),
    AWS_S3_REGION_NAME=(str, ""),
    AWS_S3_USE_SSL=(str, ""),
    AWS_STORAGE_BUCKET_NAME=(str, ""),
    AWS_ENV_FOLDER_NAME=(str, ""),
    EMAIL_HOST=(str, ""),
    EMAIL_PORT=(str, ""),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(str, ""),
    METABASE_SECRET_KEY=(str, ""),
)

# False if not in os.environ
DEBUG = env("DEBUG")
# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_DIRS = (os.path.join(BASE_DIR, "fixtures"),)

if env("TEST") is False and env("IMAGE_TAG") in ("dev", "staging", "prod"):
    image_tag = env("IMAGE_TAG")
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        environment=f"carbure-{image_tag}",
    )

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env("IMAGE_TAG") in ("dev", "staging", "prod")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = env("IMAGE_TAG") in ("dev", "staging", "prod")

OTP_EMAIL_TOKEN_VALIDITY = 1800  # 30 minutes
OTP_EMAIL_THROTTLE_FACTOR = 0  # no throttle

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django_otp",
    "django_otp.plugins.otp_email",
    "django_admin_listfilter_dropdown",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "authtools",
    "huey.contrib.djhuey",
    "core",
    "producers",
    "certificates",
    "doublecount",
    "ml",
    "saf",
    "transactions",
    "elec",
    "simple_history",
]

AUTH_USER_MODEL = "authtools.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "carbure.middlewares.spa.WhiteNoiseSPAMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "carbure.middlewares.logging.LoggingMiddleware",
    "carbure.middlewares.exception.ExceptionMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "carbure.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [env("CARBURE_HOME") + "/web/templates"],
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

WSGI_APPLICATION = "carbure.wsgi.application"

# new in django 3.2, define default type for 'id' primary key
# can also be done in each model with
# id = models.AutoField(primary_key=True)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Load db setup from DATABASE_URL env variable
DATABASES = {"default": env.db()}

DATABASES["default"]["OPTIONS"] = {
    "charset": "utf8mb4",
}

if env("TEST") == 1:
    print("DB TESTING MODE")
    DATABASES["default"]["OPTIONS"] = {
        **DATABASES["default"]["OPTIONS"],
        "auth_plugin": "mysql_native_password",
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "fr"
LANGUAGES = [
    ("fr", "Français"),
    ("en", "English"),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_L10N = True
USE_TZ = True

WHITENOISE_ALLOW_ALL_ORIGINS = False
WHITENOISE_CUSTOM_FRONTEND_ROUTING = True

if env("IMAGE_TAG") in ["dev", "staging", "prod"]:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "../front/build")]


DEFAULT_FROM_EMAIL = "noreply@carbure.beta.gouv.fr"
if env("IMAGE_TAG") in ["dev", "staging", "prod"]:
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env("EMAIL_PORT")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = env("EMAIL_USE_TLS")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
AWS_LOCATION = env("AWS_ENV_FOLDER_NAME")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "default_acl": "public-read",
            "file_overwrite": True,
            "querystring_auth": False,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATIC_URL = "/assets/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

if env("TEST") is False:
    WHITENOISE_AUTOREFRESH = True

if env("TEST"):
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",  # change debug level as appropiate
            "propagate": False,
        },
    },
}

# Huey settings
HUEY = {
    "name": "carbure",
    "huey_class": "huey.RedisHuey",
    "url": env("REDIS_URL"),
    "immediate": False,
    "consumer": {"workers": 2},
}

if DEBUG:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE += ["silk.middleware.SilkyMiddleware"]
    MIDDLEWARE.remove("csp.middleware.CSPMiddleware")

if env("IMAGE_TAG") not in ["dev", "staging", "prod"]:
    MIDDLEWARE.remove("django.middleware.csrf.CsrfViewMiddleware")

if env("TEST"):
    HUEY["immediate"] = True  # allow running background tasks immediately so we can have instant results in tests


# CSP header configuration
CSP_DEFAULT_SRC = (
    "'self'",
    "stats.beta.gouv.fr",
    "metabase.carbure.beta.gouv.fr",
    "www.data.gouv.fr",
    "https://*.tile.openstreetmap.org/",
)
CSP_EXCLUDE_URL_PREFIXES = "/admin"

# Metabase API key
METABASE_SECRET_KEY = env("METABASE_SECRET_KEY")

# Max upload size
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# Silky profiler config
SILKY_PYTHON_PROFILER = True
SILKY_ANALYZE_QUERIES = True
SILKY_AUTHENTICATION = False
SILKY_AUTHORISATION = True
SILKY_PYTHON_PROFILER = False
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_PYTHON_PROFILER_RESULT_PATH = "/tmp"


# DRF
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "core.utils.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Carbure API",
    "DESCRIPTION": "Carbure",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "DEBUG": True,
    "ENUM_NAME_OVERRIDES": {
        "saf.filters.TicketFilter.status": "saf.models.SafTicket.ticket_statuses",
        "DoubleCountingStatus": "doublecount.models.DoubleCountingApplication.DCA_STATUS_CHOICES",
        "DoubleCountingAgreementStatus": "certificates.models.DoubleCountingRegistration.AGREEMENT_STATUS",
    },
    "COMPONENT_SPLIT_REQUEST": True,
    # OTHER SETTINGS
}
