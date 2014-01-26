import urllib
import types
import cgi

from django import template


register = template.Library()


@register.simple_tag
def events_filter_url(request, filter, **kwargs):
    return cgi.escape("%s?%s" % (request.path, filter.url_query(**kwargs)))


@register.filter
def urlencode(value):
    if type(value) is types.UnicodeType:
        return urllib.quote(value.encode("utf-8"))
    else:
        return urllib.quote(value)    
