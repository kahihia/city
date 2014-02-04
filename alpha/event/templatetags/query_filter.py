import urllib
import types
import cgi

from django import template
from django.core.urlresolvers import reverse
from home.url_management.utils import url_by_identifier


register = template.Library()


@register.simple_tag
def events_filter_url(request, filter, **kwargs):
    if 'tag_page' in kwargs:
        if kwargs['tag_page']:
            path = url_by_identifier(kwargs['tag_page'])
        else:
            path = reverse('home')
    else:
        path = request.path

    return cgi.escape("%s?%s" % (path, filter.url_query(**kwargs)))


@register.filter
def urlencode(value):
    if type(value) is types.UnicodeType:
        return urllib.quote(value.encode("utf-8"))
    else:
        return urllib.quote(value)    
