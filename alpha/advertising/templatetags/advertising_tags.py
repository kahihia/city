from django import template
from django.template.base import Node, NodeList, TemplateSyntaxError
from ..models import Advertising
register = template.Library()
from django.db.models import Q


class RandomNode(Node):
    def __init__(self, nodelist_options):
        self.nodelist_options = nodelist_options

    def render(self, context):
        from random import choice
        return choice(self.nodelist_options).render(context)


def do_random(parser, token):
    """
    Output the contents of a random block.

    The `random` block tag must contain one or more `or` tags, which separate
    possible choices; a choice in this context is everything between a
    `random` and `or` tag, between two `or` tags, or between an `or` and an
    `endrandom` tag.

    Sample usage::

        {% random %}
            You will see me half the time.
        {% or %}
            You will see <em>me</em> the other half.
        {% endrandom %}
    """
    options = NodeList()

    while True:
        option = parser.parse(('or', 'endrandom'))
        token = parser.next_token()
        options.append(option)
        if token.contents == 'or':
            continue
        parser.delete_first_token()
        break
    if len(options) < 2:
        raise TemplateSyntaxError
    return RandomNode(options)

register.tag('random', do_random)


@register.inclusion_tag('advertising/advertising.html', takes_context=True)
def advertising(context, dimensions):
    """
        {% advertising "300x250" %}
    """

    width, height = map(lambda x: int(x), dimensions.split("x"))

    user_location = context.get("user_location")

    advertising_region = context.get("advertising_region", None) or user_location.get("advertising_region", None)

    region_query = Q(campaign__all_of_canada=True)

    if advertising_region:
        region_query = region_query | Q(campaign__regions=advertising_region)

    try:
        advertising = Advertising.active.filter(
            Q(ad_type__width=width), 
            Q(ad_type__height=height),
            region_query
        ).order_by('?')[0]

        advertising.view()
    except:
        advertising = None

    return {
        'advertising': advertising,
        'site': context.get("site", "")
    }


@register.inclusion_tag('advertising/advertising_group.html', takes_context=True)
def advertising_group(context, dimensions, css_class="advertising-right"):
    """
        {% advertising_group "300x250|300x250|300x250" %}

    """
    user_location = context.get("user_location")

    advertising_region = context.get("advertising_region", None) or user_location.get("advertising_region", None)

    region_query = Q(campaign__all_of_canada=True)

    if advertising_region:
        region_query = region_query | Q(campaign__regions=advertising_region)


    ads_to_return = []
    dimensions_set = dimensions.split("|")

    dimensions_hash = {}

    for dimensions in dimensions_set:
        if dimensions in dimensions_hash:
            dimensions_hash[dimensions] = dimensions_hash[dimensions] + 1
        else:
            dimensions_hash[dimensions] = 1

    for dimensions, nums in dimensions_hash.iteritems():
        width, height = map(lambda x: int(x), dimensions.split("x"))

        ads = Advertising.active.filter(
            Q(ad_type__width=width), 
            Q(ad_type__height=height),
            region_query
        ).order_by('?')[:nums]

        for ad in list(ads):
            ad.view()
            ads_to_return.append(ad)

    return {
        'ads': ads_to_return,
        'css_class': css_class
    }


@register.filter
def getbykey(dict, key):    
    return dict[key]

@register.inclusion_tag('advertising/stats/stats.html', takes_context=True)
def advertising_stats(context, ads):
    request = context["request"]
    return {
        'ads': ads,
        'request': request
    }

@register.inclusion_tag('advertising/stats/admin-advertising-list.html', takes_context=True)
def admin_advertising_stats(context, ads):
    request = context["request"]
    return {
        'ads': ads,
        'request': request
    }

@register.inclusion_tag('advertising/stats/admin-advertising-campaigns.html', takes_context=True)
def admin_advertising_campaigns(context, campaigns):
    request = context["request"]
    return {
        'campaigns': campaigns,
        'request': request
    }    