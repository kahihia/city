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
    FACEBOOK_APP_ID = '583239701740569'
    FACEBOOK_APP_SECRET = 'aae620ebe9a61c65018f17b2dfada437'
elif host_ip == '192.81.133.213':
    FACEBOOK_APP_ID = '1406987966191446'
    FACEBOOK_APP_SECRET = '349b9b850b503a02b490148333b6d917'
    GOOGLE_ANALYTICS_CODE = "UA-18720563-1"
