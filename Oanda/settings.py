"""
Django settings for Oanda project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from pytz import timezone
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@z8hw7x@tjg2wt93swr&t)f#vlky@sw(!y-1ipkt%+*)4^ei6w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',

    'apps.authentication',
    'apps.core'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'apps.authentication.middleware.AccountIdMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Oanda.urls'

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

WSGI_APPLICATION = 'Oanda.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'oanda-simulation',
#         'USER': 'abrishatlaw',
#         'PASSWORD': '9A1ciQJfbOFM',
#         'HOST': 'ep-summer-feather-438765.eu-central-1.aws.neon.tech',
#         'PORT': '',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


RES_PATH = BASE_DIR / "res/"

CURRENCY_DF_URL = "https://docs.google.com/uc?export=download&id=18BFdUu1fJCI6VmMnq_XLYwDvhdSBAEWw"
CURRENCY_DF_PATH = RES_PATH / "data/AUD-USD.csv"
SPREAD_COST_PERCENTAGE = 0.00011941434659618314
ACCOUNT_ID_KEY = "account_id"

CREATE_LOCAL_ACCOUNT = True
MANUAL_TIME_SELECTION = False

START_TIME_ENV_KEY = 'OANDA_LOCAL_DEFAULT_ACCOUNT_START_TIME'
START_TIME_FILE_PATH = RES_PATH / "local_default_account_start_time.json"

TIMES_LIST_FILE = RES_PATH / "times/times-5.json"

if MANUAL_TIME_SELECTION:
    print('Using manual time selection')
    with open(TIMES_LIST_FILE, 'r') as f:
        os.environ[START_TIME_ENV_KEY] = random.choice(json.load(f))

LOCAL_DEFAULT_ACCOUNT_START_TIME = os.environ.get(
    START_TIME_ENV_KEY,
    None
)
if LOCAL_DEFAULT_ACCOUNT_START_TIME is not None:
    LOCAL_DEFAULT_ACCOUNT_TIME_DELTA = int(
        (
                datetime.now().replace(tzinfo=timezone("UTC")) - datetime.strptime(LOCAL_DEFAULT_ACCOUNT_START_TIME, '%Y-%m-%d %H:%M:%S%z')
        ).total_seconds()//60
    )
else:
    LOCAL_DEFAULT_ACCOUNT_TIME_DELTA = random.randint(*[
        (datetime.now().replace(tzinfo=timezone("UTC")) - datetime.strptime(t, '%Y-%m-%d %H:%M:%S%z')).total_seconds()//60
        for t in ['2024-05-19 18:16:00+00:00', '2023-10-15 00:01:00+00:00']
    ])
print('Using local account with time delta', LOCAL_DEFAULT_ACCOUNT_TIME_DELTA)
print('Using start time', datetime.now() - timedelta(minutes=LOCAL_DEFAULT_ACCOUNT_TIME_DELTA))
LOCAL_DEFAULT_ACCOUNT_DELTA_MULTIPLIER = 10.0
LOCAL_DEFAULT_ACCOUNT_BALANCE = 100.0
LOCAL_DEFAULT_ACCOUNT_FILE_PATH = RES_PATH / "local_account.json"


PRICE_CACHING_TIMEOUT = 30
MIN_GRANULARITY = 1

STATS_DUMP_PATH = RES_PATH / "stats" / f"{datetime.now().timestamp()}.json"
