from django import template


register = template.Library()


special_keys = ["today", "tomorrow", "this-weekend", "next-week"]


@register.simple_tag
def events_filter_url(request, filter, **kwargs):
    return "%s?%s" % (request.path, filter.url_query(**kwargs))
