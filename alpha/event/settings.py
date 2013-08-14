from django.conf import settings

DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', u'noreply@cityfusion.ca')
EVENT_PICTURE_DIR = getattr(settings, 'EVENT_PICTURE_DIR', 'pictures')
FACEBOOK_PAGE_ID = getattr(settings, 'FACEBOOK_PAGE_ID', '523227901077594')
EVENTFUL_ID = getattr(settings, 'EVENTFUL_ID', '294833066685')
CONCERTIN_ID = getattr(settings, 'CONCERTIN_ID', '229535758760')