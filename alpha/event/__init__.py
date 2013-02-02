from django.conf import settings
from PIL import Image

#used in views
EVENTS_PER_PAGE = getattr(settings, 'EVENTS_PER_PAGE', 2)
DEFAULT_FROM_EMAIL = getattr(settings,'DEFAULT_FROM_EMAIL', u'noreply@peakxp.com')
#used in event_pictures
EVENT_DEFAULT_PICTURE_URL = getattr(settings, 'EVENT_DEFAULT_PICTURE_URL',
                                    settings.STATIC_URL + 'img/placeholder.svg')
#used in models
EVENT_PICTURE_DIR = getattr(settings, 'EVENT_PICTURE_DIR', 'pictures')
EVENT_RESIZE_METHOD = getattr(settings, 'EVENT_RESIZE_METHOD', Image.BICUBIC)
EVENT_DEFAULT_SIZES = getattr(settings, 'EVENT_DEFAULT_SIZES', (40,))

