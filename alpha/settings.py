# local dev settings

from common_settings import *
import socket

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'cityfusion_dev',                      # Or path to database file if using sqlite3.
        'USER': 'cityfusion_dev',                      # Not used with sqlite3.
        'PASSWORD': 'forfusion',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

host_ip = socket.gethostbyname(socket.gethostname())

if host_ip == '127.0.0.1':
    FACEBOOK_APP_ID = '536513936402579'
    FACEBOOK_APP_SECRET = 'f0aea33f1319a8e238a419ea57a671d5'

elif host_ip == '192.81.133.213':
    FACEBOOK_APP_ID = '1406987966191446'
    FACEBOOK_APP_SECRET = '349b9b850b503a02b490148333b6d917'
    GOOGLE_ANALYTICS_CODE = 'UA-43571619-1'

    TWILIO_ACCOUNT_SID = 'ACe1055ea325ab5273147cab8ee7f0a856'
    TWILIO_AUTH_TOKEN = '11743ce6dbac27165c433e2fe901383b'
    TWILIO_NUMBER = "+13069883370"

    MAMONA_BACKENDS_SETTINGS = {
        'paypal': {
            'url': 'https://www.paypal.com/cgi-bin/webscr',
            'email': 'ray@cityfusion.ca',
        }
    }