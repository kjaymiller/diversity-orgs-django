"""
Django settings for diversity_orgs project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
from django.forms.renderers import TemplatesSetting

class CustomFormRenderer(TemplatesSetting):
    form_template_name = "/forms/org_forms.html"


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", False)

ADMIN_ENABLED = os.environ.get("DJANGO_ADMIN_ENABLED", False)

ALLOWED_HOSTS = SITE_HOSTS = (
    "diversityorgs.tech",
    "diversityorgs-django.azurewebsites.net",
    "localhost",
    "127.0.0.1",
)

# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.forms",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "org_pages.apps.OrgPagesConfig",  # Orgs
    "accounts",  # Accounts App,
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True

# CORS_ORIGIN_WHITELIST = (
#        'https://diversityorgsstorage.blob.core.windows.net',
# )

ROOT_URLCONF = "diversity_orgs.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

FORM_RENDERER = "diversity_orgs.settings.CustomFormRenderer"

WSGI_APPLICATION = "diversity_orgs.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ]
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
db_host = f"{os.environ.get('POSTGRES_DBHOST')}.postgres.database.azure.com"

if not os.environ.get("POSTGRES_DBHOST", None):
    db_host = "localhost"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DBNAME", "test_db_admin"),
        "USER": os.environ.get("POSTGRES_DBUSER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_DBPASS", "password"),
        "HOST": db_host,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

AZURE_ACCOUNT_NAME = os.environ.get("AZ_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_KEY = os.environ.get("AZ_STORAGE_KEY", False)
AZURE_MEDIA_CONTAINER = os.environ.get("AZURE_MEDIA_CONTAINER", "media")
AZURE_STATIC_CONTAINER = os.environ.get("AZURE_STATIC_CONTAINER", "static")
MEDIA_URL = os.environ.get("AZ_MEDIA_URL", "media")
DEFAULT_FILE_STORAGE = "backend.azurestorage.AzureMediaStorage"
STATICFILES_STORAGE = "backend.azurestorage.AzureStaticStorage"
STATIC_URL = os.environ.get("AZ_STATIC_URL", "/static/")
STATIC_ROOT = BASE_DIR / "static"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AZURE_MAPS_KEY = os.environ.get("AZURE_MAPS_KEY", False)
AUTH_USER_MODEL = "accounts.CustomUser"

# HTTPS PROXY TO FIX CSRF ISSUES
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# django_project/settings.py
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"  # new