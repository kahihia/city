import os.path
import djcelery
djcelery.setup_loader()
# Django settings for alpha project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('jaromudr', 'jaromudr@gmail.com'),
    ('tim', 'tim@cityfusion.ca'),
    ('igor', 'info@silkcode.com'),
)

MANAGERS = ADMINS

BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name although not
# all choices may be available on all operating systems.  On Unix
# systems, a value of None will cause Django to use the same timezone
# as the operating system.  If running in a Windows environment this
# must be set to the same as your system time zone.
TIME_ZONE = 'America/Regina'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as
# not to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold
# user-uploaded files.  Example:
# "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use
# a trailing slash.  Examples: "http://media.lawrence.com/media/",
# "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static
# files in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or
    # "C:/www/django/static".  Always use forward slashes, even on
    # Windows.  Don't forget to use absolute paths, not relative
    # paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5=g^q+(_5rk4_r9%n8)2&cg1oqi05)l4w%%fs8%mc+$l&jeseh'

# List of callables that know how to import templates from various
# sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
from django.conf import global_settings

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    # required by django-admin-tools
    'django.core.context_processors.request',
    'event.context_processors.nearest_locations',
    'django_facebook.context_processors.facebook',
)

ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'event.middleware.LocationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".  Always use forward slashes, even on
    # Windows.  Don't forget to use absolute paths, not relative
    # paths.
)

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    'citi_user',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.gis',
    'cities',
    'selectable',
    'registration',
    'south',
    'taggit',
    'taggit_autosuggest',
    'event',
    'home',
    'feedback',
    'easy_thumbnails',
    'image_cropping',
    'ajaxuploader',
    'endless_pagination',
    'django_filters',
    'guardian',
    'accounts',
    'userena',
    'django_facebook',
    'djcelery',
)

# A sample logging configuration. The only tangible logging performed
# by this configuration is to send an email to the site admins on
# every HTTP 500 error.  See
# http://docs.djangoproject.com/en/dev/topics/logging for more details
# on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'cities': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 3355


# django.registration settings, one week window to activate
ACCOUNT_ACTIVATION_DAYS = 7

# django auth settings
LOGIN_REDIRECT_URL = '/events/'

# django taggit settings

# alpha.event settings
# EVENT_PICTURE_DIR #defaults to 'pictures'
EVENT_DEFAULT_PICTURE_URL = STATIC_URL + 'img/default.gif'
# EVENT_RESIZE_METHOD #defaults to Image.BICUBIC (cubic spline
#                      interpolation in a 4x4 environment), can be
#                      Image.NEAREST (use nearest neighbour),
#                      Image.ANTIALIAS (a high-quality downsampling
#                      filter), or Image.BILINEAR (linear
#                      interpolation in a 2x2 environment)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EVENT_EMAIL_SITE = 'dev.cityfusion.ca'
#instead of taking the hustles of configuring a simple mail server, use an established one instead

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'cityfusion.smtp@gmail.com'
EMAIL_HOST_PASSWORD = 'forfusion'
EMAIL_PORT = 587

CITIES_FILES = {
    'city': {
       'filename': 'CA.zip',
       'urls':     ['http://download.geonames.org/export/dump/CA.zip']
    }
}

CITIES_POSTAL_CODES = ['CA']
CITIES_LOCALES = ['en', 'und', 'LANGUAGES']
CITIES_PLUGINS = [
    'cities.plugin.postal_code_ca.Plugin',  # Canada postal codes need region codes remapped to match geonames
]

SELECTABLE_MAX_LIMIT = 10

from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS

GEOIP_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geoip'))

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'django_facebook.auth_backends.FacebookBackend',
)

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'
USERENA_REDIRECT_ON_SIGNOUT = "/events/"

ANONYMOUS_USER_ID = -1

AUTH_PROFILE_MODULE = 'accounts.Account'

FACEBOOK_APP_ID = "241160805895511"
FACEBOOK_APP_SECRET = "aacc6191a48ff2c251f6e69b1d4ba1c1"
# FACEBOOK_REGISTRATION_BACKEND = 'django_facebook.registration_backends.UserenaBackend'
AUTH_PROFILE_MODULE = 'accounts.Account'

BROKER_URL = 'amqp://guest:guest@localhost:5672/'


from datetime import timedelta
from celery.schedules import crontab

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

CELERYBEAT_SCHEDULE = {
    'reminding-about-events-every-5-minutes': {
        'task': 'accounts.tasks.remind_accounts_about_events',
        'schedule': timedelta(minutes=30)
    },
    'reminding-about-event-every-day': {
        'task': 'accounts.tasks.remind_accounts_about_events_on_week_day',
        'schedule': crontab(hour=6, minute=0),
    },
    'inform-accounts-about-new-events-with-tags-every-3-hours': {
        'task': 'accounts.tasks.inform_accounts_about_new_events_with_tags',
        'schedule': timedelta(minutes=1)
        # 'schedule': crontab(hours=6)
    }
}

CELERY_TIMEZONE = 'UTC'
