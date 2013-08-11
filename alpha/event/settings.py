from django.conf import settings

DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', u'noreply@cityfusion.ca')
EVENT_PICTURE_DIR = getattr(settings, 'EVENT_PICTURE_DIR', 'pictures')