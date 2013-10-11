from django.conf import settings

DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', u'noreply@cityfusion.ca')

EVENT_PICTURE_DIR = getattr(settings, 'EVENT_PICTURE_DIR', 'pictures')
EVENT_ATTACHMENT_DIR = getattr(settings, 'EVENT_ATTACHMENT_DIR', 'attachments')

FACEBOOK_PAGE_ID = getattr(settings, 'FACEBOOK_PAGE_ID', '638979249459268')

EVENTFUL_ID = getattr(settings, 'EVENTFUL_ID', '294833066685')

CONCERTIN_ID = getattr(settings, 'CONCERTIN_ID', '229535758760')

DELETED_EVENTS_REMINDING_INTERVAL = getattr(settings, 'DELETED_EVENTS_REMINDING_INTERVAL', 5)