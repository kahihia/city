# prod server settings

from common_settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'cityfusion',                      # Or path to database file if using sqlite3.
        'USER': 'cityfusion',                      # Not used with sqlite3.
        'PASSWORD': 'Tt5loh6RWrae',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'CityFusion Mailer <automaton@cityfusion.ca>'
#EMAIL_HOST = '50.116.14.210'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'arlusishmael@gmail.com'
EMAIL_HOST_PASSWORD = '19553b2008'


DEBUG = False
TEMPLATE_DEBUG = DEBUG

# alpha.event settings
EVENTS_PER_PAGE = 30
