import urllib
import re

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def html_urlize(value):
    pattern = re.compile(r'(^|[>\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)',
                         re.IGNORECASE | re.DOTALL)
    return pattern.sub(r'\1<a href="\2">\2</a>', value)


@register.filter
def none_convert(value):
    if value is None:
        return ''
    return value


@register.filter
def shorten_string(value, length):
    if len(value) > length:
        return '%s...' % value[:length]

    return value


@register.simple_tag(takes_context=True)
def like_button(context, url):
    return '<iframe src="https://www.facebook.com/plugins/like.php?locale=en_US&amp;href=%s&amp;width=93' \
           '&amp;height=21&amp;colorscheme=light&amp;layout=button_count&amp;action=like&amp;show_faces=false' \
           '&amp;send=false&amp;appId=%s" scrolling="no" frameborder="0" style="border:none; ' \
           'overflow:hidden; width:82px; height:21px; vertical-align: middle;" allowTransparency="true">' \
           '</iframe>' % (urllib.quote(url), settings.FACEBOOK_APP_ID)


def callMethod(obj, methodName):
    method = getattr(obj, methodName)

    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()


def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []

    obj.__callArg += [arg]
    return obj

register.filter("call", callMethod)
register.filter("args", args)