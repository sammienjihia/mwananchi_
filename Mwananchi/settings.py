"""
Django settings for BrandSense project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k$j)c7=8xvj3!u3oc%r$0ddd#y7)%wx$(*!xrq0x^bxeeav=kh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['159.65.38.151']

MEDIA_ROOT = os.path.join(BASE_DIR, 'MEDIA_FILES/')
MEDIA_URL = 'MEDIA_FILES/'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts.apps.AccountsConfig',

    'client.apps.AspirantConfig',
    'celery_stuff.apps.CeleryStuffConfig',
    'site_admin.apps.SiteAdminConfig',
    'volunteer.apps.VolunteerConfig',

    'twitter.apps.TwitterConfig',

    'seats.apps.SeatsConfig',
    'sms.apps.SmsConfig',
    'subscribers.apps.SubscribersConfig',

    'language.apps.LanguageConfig',
    'campaign.apps.ManifestoConfig',

    'survey.apps.SurveyConfig',
    'subscriber_details_survey.apps.SubscriberDetailsSurveyConfig',

    'region.apps.RegionConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Mwananchi.urls'

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

WSGI_APPLICATION = 'Mwananchi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mwananchi_db',
        'USER': 'mwananchi_db',
        'PASSWORD': 'mwananchi_db',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


# Email settings

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'techgravellian@gmail'
EMAIL_HOST_PASSWORD = 'PsWd@&123#@spoof'
EMAIL_PORT = '465'
EMAIL_USE_TLS = True
# 587

# CELERY STUFF
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
#CELERY_TRACK_STARTED = True


#Twitter
TWITTER_TOKEN = 'DASDze82n52S1mWqjaABSOFZD'
TWITTER_SECRET = 'VjDDbowV4qEHdn0v5f8IkiWNwzYlozmww11fularNSpF1t4jqD'

# Pagination settings
PAGINATION_OFFSET = 50

# Sms settings

SMS_SHORT_CODE = '1234'
SMS_USER_NAME = ''
SMS_API_KEY = ''




