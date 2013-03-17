from django import template

from event import EVENT_DEFAULT_PICTURE_URL
from event.models import Event

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

register = template.Library()


def event_picture_url(event, size=40):
    if not(isinstance(event, Event)):
        return EVENT_DEFAULT_PICTURE_URL
    if not event.picture:
        return EVENT_DEFAULT_PICTURE_URL
    if not event.picture_exists(size):
        event.create_resized(size)
    return event.picture_url(size)
register.simple_tag(event_picture_url)


@register.simple_tag
def if_url(value, if_passed, if_failed):
    val = URLValidator()
    try:
        val(value)
        return if_passed
    except ValidationError:
        return if_failed
