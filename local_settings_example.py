# An example file demonstrating what the minimum local_settings.py should contain.
# The values here are not suitable for a production environment. 
# When deploying this site, a production database such as mySQL or Postrgres should be used instead of sqlite.
# We recommend running Django's built in deployment check via 'python manage.py check --deploy'

DEBUG = True # Gives lots of details when something goes wrong. Only set to True for development

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