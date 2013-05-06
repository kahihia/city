from django import template

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from easy_thumbnails.files import get_thumbnailer
import Image
import ImageDraw
import ImageFont
from django.template import defaultfilters as filters
import StringIO
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

register = template.Library()


@register.simple_tag
def if_url(value, if_passed, if_failed):
    val = URLValidator()
    try:
        val(value)
        return if_passed
    except ValidationError:
        return if_failed


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


@register.simple_tag
def feature_event_as_image(event):
    # TODO: use existing image if it is possible, while I test email it is good that image render on request
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
    else:
        thumb = "event/static/images/default-event-147x147.jpg"

    im = Image.open(thumb)
    im = im.convert("RGBA")

    bottom_bg = Image.new("RGBA", (147, 57), (0, 0, 0, 200))

    im.paste(bottom_bg.convert('RGB'), (0, 90), bottom_bg)

    draw = ImageDraw.Draw(im)

    event_name_pos = (5, 95)
    start_time_pos = (5, 108)
    venue_pos = (5, 121)
    event_details_pos = (5, 131)

    arial = ImageFont.truetype("%s/event/static/fonts/Arial.ttf" % settings.BASE_PATH, 10)
    arial_bold = ImageFont.truetype("%s/event/static/fonts/Arial_Bold.ttf" % settings.BASE_PATH, 10)

    time_period = "%s - %s" % (filters.title(filters.date(event.nearest_start_time, "b d, Y | fA")), filters.title(filters.date(event.nearest_end_time, "fA")))

    draw.text(event_name_pos, truncatesmart(event.name, 25), (235, 138, 25), font=arial_bold)
    draw.text(start_time_pos, truncatesmart(time_period, 25), (255, 255, 255), font=arial)
    draw.text(venue_pos, truncatesmart(event.venue.name, 25), (255, 255, 255), font=arial)
    draw.text(event_details_pos, "event details", (36, 124, 195), font=arial_bold)

    content = StringIO.StringIO()
    im.save(content, 'PNG')

    in_memory_file = InMemoryUploadedFile(content, None, "%s_feature_event_as_image.png" % event.slug, "image/png", content.len, None)

    feature_event_image = default_storage.save("%s_feature_event_as_image.png" % event.slug, in_memory_file)

    return "/media/%s" % feature_event_image
