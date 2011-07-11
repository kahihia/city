from django import template

from event import EVENT_DEFAULT_PICTURE_URL
from event.models import Event

register = template.Library()

def event_picture_url(event, size=40):
    if not(isinstance(event,Event)):
        return EVENT_DEFAULT_PICTURE_URL
    if not event.picture:
        return EVENT_DEFAULT_PICTURE_URL
    if not event.picture_exists(size):
        event.create_resized(size)
    return event.picture_url(size)
register.simple_tag(event_picture_url)
