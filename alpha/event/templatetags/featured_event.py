from event.models import FeaturedEvent
from django import template
from easy_thumbnails.files import get_thumbnailer
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from django.template import defaultfilters as filters
import StringIO
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.db.models import F

register = template.Library()


@register.inclusion_tag('featured/featured_events.html', takes_context=True)
def featured_events_container(context, events, in_email=False):
    FeaturedEvent.objects.filter(event_id__in=[event.id for event in events]).update(views=F('views')+1)

    return {
        'events': events,
        'in_email': in_email,
        'site': context.get("site", "")
    }

@register.inclusion_tag('featured/featured_event.html', takes_context=True)
def featured_event(context, event, in_email=False):
    FeaturedEvent.objects.filter(event_id=event.id).update(views=F('views')+1)

    return {
        'event': event,
        'in_email': in_email,
        'site': context.get("site", "")
    }

@register.inclusion_tag('events/list/featured_event_link.html', takes_context=True)
def featured_event_link(context, event):
    return {
        'event': event
    }    


def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Make sure it's unicode
    value = unicode(value)

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    return value + '...'


@register.simple_tag(takes_context=True)
def feature_event_as_image(context, event):
    script_version = "1.02"

    image_filename = "%s_feature_event_as_image_%s.png" % (event.slug, script_version)

    if not default_storage.exists(image_filename):
        size = (147, 147)
        if event.picture:
            thumbnailer = get_thumbnailer(event.picture)
            thumbnail_options = {
                'size': size,
                'box': event.cropping,
                'crop': True,
                'detail': True,
                'upscale': False
            }
            thumb = thumbnailer.get_thumbnail(thumbnail_options)
            im = thumb.image
        else:
            im = Image.open("event/static/images/default-event-147x147.jpg")
        
        im = im.convert("RGBA")

        bottom_bg = Image.new("RGBA", (147, 57), (0, 0, 0, 200))

        im.paste(bottom_bg.convert('RGB'), (0, 90), bottom_bg)

        draw = ImageDraw.Draw(im)

        event_name_pos = (5, 95)
        start_time_pos = (5, 108)
        venue_pos = (5, 121)
        event_details_pos = (5, 131)

        arial = ImageFont.truetype("%s/alpha/event/static/fonts/Arial.ttf" % settings.BASE_PATH, 10)
        arial_bold = ImageFont.truetype("%s/alpha/event/static/fonts/Arial_Bold.ttf" % settings.BASE_PATH, 10)

        time_period = "%s - %s" % (filters.title(filters.date(event.start_time, "b d, Y | fA")), filters.title(filters.date(event.end_time, "fA")))

        draw.text(event_name_pos, truncatesmart(event.name, 25), (235, 138, 25), font=arial_bold)
        draw.text(start_time_pos, truncatesmart(time_period, 25), (255, 255, 255), font=arial)
        draw.text(venue_pos, truncatesmart(event.venue.name, 25), (255, 255, 255), font=arial)
        draw.text(event_details_pos, "event details", (36, 124, 195), font=arial_bold)

        content = StringIO.StringIO()
        im.save(content, 'PNG')

        in_memory_file = InMemoryUploadedFile(content, None, image_filename, "image/png", content.len, None)

        image_filename = default_storage.save(image_filename, in_memory_file)


    return "media/%s" % image_filename
