"""
Django settings for Warm Hook Hugs — config project.
=====================================================
Premium handcrafted crochet & knitwear e-commerce platform.

Dev  : SQLite + DEBUG=True
Prod : PostgreSQL + Gunicorn + Nginx (see docker-compose.yml)
"""

import os
from pathlib import Path
from decouple import config, Csv

# ──────────────────────────────────────────────
# BASE DIRECTORY
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-only-change-me-in-production-!!!')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:8000', cast=Csv())

# ──────────────────────────────────────────────
# INSTALLED APPS
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    # Local apps
    'store',
]

# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ──────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_item_count',
                'store.context_processors.wishlist_count',
                'store.context_processors.global_forms',
                'store.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ──────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────
# Dev: SQLite | Prod: set DATABASE_URL env var for PostgreSQL
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}

# ──────────────────────────────────────────────
# AUTH PASSWORD VALIDATORS
# ──────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# STATIC & MEDIA FILES
# ──────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────────
# DEFAULT PK TYPE
# ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────
# SESSION CONFIG (used for cart + OTP)
# ──────────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours

# ──────────────────────────────────────────────
# OTP SETTINGS
# ──────────────────────────────────────────────
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6

# ──────────────────────────────────────────────
# OTP PROVIDER: 'console' (dev) or 'whatsapp' (prod)
# ──────────────────────────────────────────────
OTP_PROVIDER = config('OTP_PROVIDER', default='console')

# ──────────────────────────────────────────────
# WHATSAPP BUSINESS API (Meta Cloud API)
# ──────────────────────────────────────────────
WHATSAPP_PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default='DUMMY_PHONE_ID_123456')
WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN', default='DUMMY_ACCESS_TOKEN_REPLACE_ME')
WHATSAPP_API_VERSION = config('WHATSAPP_API_VERSION', default='v18.0')

# ──────────────────────────────────────────────
# PAYMENT GATEWAYS (replace with real credentials)
# ──────────────────────────────────────────────
# Card Payments (Stripe / HBL / any PSP) — set in .env
PAYMENT_CARD_PROVIDER = config('PAYMENT_CARD_PROVIDER', default='stripe')  # stripe | hbl | paymob
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='pk_test_DUMMY_REPLACE_ME')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_DUMMY_REPLACE_ME')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# EasyPaisa — set in .env
EASYPAISA_STORE_ID = config('EASYPAISA_STORE_ID', default='DUMMY_STORE_ID')
EASYPAISA_HASH_KEY = config('EASYPAISA_HASH_KEY', default='DUMMY_HASH_KEY')
EASYPAISA_ENVIRONMENT = config('EASYPAISA_ENVIRONMENT', default='sandbox')  # sandbox | production

# JazzCash — set in .env
JAZZCASH_MERCHANT_ID = config('JAZZCASH_MERCHANT_ID', default='DUMMY_MERCHANT_ID')
JAZZCASH_PASSWORD = config('JAZZCASH_PASSWORD', default='DUMMY_PASSWORD')
JAZZCASH_INTEGRITY_SALT = config('JAZZCASH_INTEGRITY_SALT', default='DUMMY_SALT')
JAZZCASH_ENVIRONMENT = config('JAZZCASH_ENVIRONMENT', default='sandbox')  # sandbox | production

# ──────────────────────────────────────────────
# EMAIL CONFIGURATION
# ──────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Warm Hook Hugs <hello@warmhookhugs.pk>')

# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/'
LOGOUT_REDIRECT_URL = '/'

# ──────────────────────────────────────────────
# ANALYTICS (set in .env for production)
# ──────────────────────────────────────────────
GA4_MEASUREMENT_ID = config('GA4_MEASUREMENT_ID', default='')
META_PIXEL_ID = config('META_PIXEL_ID', default='')

# ──────────────────────────────────────────────
# PRODUCTION HARDENING (only when DEBUG=False)
# ──────────────────────────────────────────────
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
