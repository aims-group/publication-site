import os

DEBUG = os.environ.get("DJANGO_DEBUG", False)
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

CSRF_COOKIE_HTTPONLY = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'publisher',
    'django_recaptcha',
    'widget_tweaks',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'publisher.processors.nav_options',
                'publisher.processors.pending_dois'
            ],
        },
    },
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

ROOT_URLCONF = 'admin.urls'

WSGI_APPLICATION = 'admin.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "applogfile": {
            "level": os.environ.get("DJANGO_LOGGING_LEVEL", default="INFO"),
            "class": "logging.handlers.RotatingFileHandler",
            "filename":  os.environ.get("DJANGO_LOGGING_FILENAME", default="/var/log/publications-site.log"),
            "maxBytes": 1024 * 1024 * 15,
            "backupCount": 10
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["applogfile"],
            "level": os.environ.get("DJANGO_LOGGING_LEVEL", default="INFO"),
            "propagate": True
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True


USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# Set prefix of URL if site is served from a subdirectory 
# (i.e. If the site is served from my.site.com/pubhub, then set URL_PREFIX = '/pubhub'.)
URL_PREFIX = ''

STATIC_ROOT = 'static'

STATIC_URL = '{}/static/'.format(URL_PREFIX)

LOGIN_REDIRECT_URL = '{}/'.format(URL_PREFIX)

LOGIN_URL = '{}/accounts/login/'.format(URL_PREFIX)

# Django Admin URL.
ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL", default="admin/")

STATICFILES_DIRS = (
    'pubhub-static',
)

# Google's recaptcha. Refer to the recaptcha web site for this key https://www.google.com/recaptcha/intro/
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY", default='')
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY", default='')

# Email values must be set for password recovery to function
EMAIL_HOST = os.environ.get("EMAIL_HOST", default='localhost')
EMAIL_PORT = os.environ.get("EMAIL_PORT", default=1025)
