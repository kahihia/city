# local dev settings

from common_settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'cityfusion_dev',                      # Or path to database file if using sqlite3.
        'USER': 'cityfusion_dev',                      # Not used with sqlite3.
        'PASSWORD': 'forfusion',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# alpha.event settings
EVENTS_PER_PAGE = 2
#added by aurlus
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'arlusishmael@gmail.com'
#EMAIL_HOST_PASSWORD = '19553b2008'
#EMAIL_PORT = 587


