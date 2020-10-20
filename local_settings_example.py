# An example file demonstrating what the minimum local_settings.py should contain.
# The values here are not suitable for a production environment. 
# When deploying this site, a production database such as mySQL or Postrgres should be used instead of sqlite.
# We recommend running Django's built in deployment check via 'python manage.py check --deploy'
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # Gives lots of details when something goes wrong. Only set to True for development

ALLOWED_HOSTS = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

# sqlite is the quick an easy development db
DATABASES = {
  'default': {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME': 'local.db',
      'USER': '',             # Not used with sqlite3.
      'PASSWORD': '',         # Not used with sqlite3.
      'HOST': '',             # Not used with sqlite3.
      'PORT': '',             # Not used with sqlite3.
  }
}

SECRET_KEY = "}.!CLP*DF.CY=|DY<>~56?2N0I~UF^O>40'M|Y!)%E>6%<'95N" # Used by danjo for cryptographic signing. Set this to a unique random value
RECAPTCHA_PUBLIC_KEY = "" # Google's recaptcha. Refer to the recaptcha web site for this key
RECAPTCHA_PRIVATE_KEY = "" # https://www.google.com/recaptcha/intro/

EMAIL_HOST = 'localhost' # Email values must be set for password recovery to function
EMAIL_PORT = 1025

# Set prefix of URL if site is served from a subdirectory 
# (i.e. If the site is served from my.site.com/pubhub, then set URL_PREFIX = '/pubhub'.)
URL_PREFIX = ''

os.environ["REQUESTS_CA_BUNDLE"] = "/absolute/path/to/certfile.crt"  
# Path to the .crt file. 
# Used if the server is behind a corporate firewall that intercepts ssl
# This can be set to "" (empty string) if your server is not behind one of these annoying firewalls
