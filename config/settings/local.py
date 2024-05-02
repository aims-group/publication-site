import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", default='29l93ms9m32390#20-z!32ad38')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', default=''),
        'USER': os.environ.get('POSTGRES_USER', default=''),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', default=''),
        'HOST': os.environ.get('POSTGRES_HOST', default=''),
        'PORT': os.environ.get('POSTGRES_PORT', default=''),
    }
}

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
] + INSTALLED_APPS
