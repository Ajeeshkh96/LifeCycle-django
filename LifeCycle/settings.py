"""
Django settings for LifeCycle project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "django-insecure-sleim+5$5p$up6$5b#89eqgvcq)z&zyrot%(zwul**l=sr0@x^"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: list[str] = []


# ALLOWED_HOSTS = ['3.81.185.202', '0.0.0.0', 'localhost']

# CSRF_TRUSTED_ORIGINS = ['http://3.81.185.202', 'http://0.0.0.0']


# Application definition

INSTALLED_APPS = [
    "users",
    "carts",
    "orders",
    "offers",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # paypal integration
    "paypal.standard.ipn",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "LifeCycle.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "users.context_processor.menu_links",
                "users.context_processor.menu_links1",
                "carts.context_processor.counter",
            ],
        },
    },
]

WSGI_APPLICATION = "LifeCycle.wsgi.application"

AUTH_USER_MODEL = "users.Account"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "LifeCycle",
        "USER": "postgres",
        "PASSWORD": "Ajeeshkh786@",
        "HOST": "localhost",
        "PORT": "5432",
    }
}



# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "LifeCycle",
#         "USER": "postgres",
#         "PASSWORD": "Ajeeshkh786",
#         "HOST": "kart.cwgglaydlgdw.us-east-1.rds.amazonaws.com",
#         "PORT": "5432",
#     }
# }



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [
    "LifeCycle/static",
]

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Emailing settings
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "muhammedajeesh111@gmail.com"
EMAIL_HOST_PASSWORD = "hwqxywygjdrwides"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# PASSWORD_RESET_TIMEOUT = 14400

# Mobile OTP
TWILIO_ACCOUNT_SID = "AC55cb7607c8851d080b10a7cf80922cae"
TWILIO_AUTH_TOKEN = "0f5c0520e8436fea1203fc679f7d0390"
# TWILIO_PHONE_NUMBER = "+16818811751"  # This is your Twilio phone number
TWILIO_VERIFY_SID = "VAbbd8b448dce3db695c89cdb6e2244889"


# payment integration
PAYPAL_RECEIVER_EMAIL = "lifecycle.businesssandbox@gmail.com"
PAYPAL_TEST = True


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}


LOGIN_URL = "login"
