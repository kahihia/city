from django.conf import settings
from PIL import Image

from event.models import Event
from django.db.models import signals

#used in views.browse
EVENTS_PER_PAGE = getattr(settings, 'EVENTS_PER_PAGE', 5)
#used in event_pictures
EVENT_DEFAULT_PICTURE_URL = getattr(settings, 'EVENT_DEFAULT_PICTURE_URL',
                                    STATIC_URL + 'img/placeholder.svg')
#used in utils.picture_file_path and models.Event
EVENT_PICTURE_DIR = getattr(settings, 'EVENT_PICTURE_DIR', 'pictures')
#used in models.Event
EVENT_RESIZE_METHOD = getattr(settings, 'EVENT_RESIZE_METHOD', Image.BICUBIC)
#used here
EVENT_DEFAULT_SIZES = getattr(settings, 'EVENT_DEFAULT_SIZES', (40,))

def create_default_pictures(event=None, created=False, **kwargs):
    if created:
        for size in EVENT_DEFAULT_SIZES:
            instance.create_resized(size)
signals.post_save.connect(create_default_pictures, sender=Event)
