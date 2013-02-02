# dev server settings

from common_settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'cityfusion_dev',                      # Or path to database file if using sqlite3.
        'USER': 'cityfusion_dev',                      # Not used with sqlite3.
        'PASSWORD': 'tk2A0RB1Iqfm',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#DEFAULT_FROM_EMAIL = 'Cityfusion Mailer <dev-automaton@cityfusion.ca>'
#EMAIL_HOST = '10.181.225.239'

#EVENT_EMAIL_SITE = 'cityfusion.dev.peakxp.com'

# alpha.event settings
EVENTS_PER_PAGE = 20

#instead of taking the hustles of configuring a simple mail server, use an established one instead

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'arlusishmael@gmail.com'
EMAIL_HOST_PASSWORD = '19553b2008'
EMAIL_PORT = 587
