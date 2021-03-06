"""
Django settings for vms project.

Note: Currently development settings. Not suitable as is for production.
"""
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY ='_9@_o4s(*=qz5i&i@6f_!jg#1o4ptqwz#s4d#s%(j*i^juq!%('

# SECURITY WARNING: run with debug turned off (DEBUG = False) in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []
ROOT_URLCONF = 'vms.urls'
# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'administrator',
    'authentication',
    'event',
    'home',
    'job',
    'organization',
    'registration',
    'shift',
    'vms',
    'volunteer',
    'cities_light',
    'pom',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'vms.urls'

WSGI_APPLICATION = 'vms.wsgi.application'

# Database
# Change these database settings if your database engine, database name,
# username or password changes
DATABASES = {
      'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'vms.db'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale/'), )

LANGUAGES = (
    ('en-us', _('English')),
    ('fr-fr', _('French')),
)

# Static files (CSS, JavaScript, Images)
# Specifies the directory where static files (CSS, JavasScript) are stored
STATIC_URL = '/static/'

# All uploaded files (such as resumes) are stored in the /srv directory
# /srv directory contains site-specific data which is served by the system
MEDIA_ROOT = os.path.join(BASE_DIR)
MEDIA_URL = '/srv/'

# Uploaded files have read and write permissions to the owner only
FILE_UPLOAD_PERMISSIONS = 0o600

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o600

# If user fails to authenticate, then they are redirected to the view
# specified in the reverse_lazy call
LOGIN_URL = reverse_lazy('authentication:login_process')

STATIC_ROOT = './static/'

LOGIN_REDIRECT_URL = reverse_lazy('home:index')
RECOVER_ONLY_ACTIVE_USERS = False
ACCOUNT_ACTIVATION_DAYS = 2
ANONYMOUS_USER_ID = -1
