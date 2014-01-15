from django import template
from django.template.base import Node, NodeList, TemplateSyntaxError
from ..models import Advertising
register = template.Library()
from django.db.models import Q, F
from random import choice
from collections import OrderedDict


class RandomNode(Node):
    def __init__(self, nodelist_options):
        self.nodelist_options = nodelist_options

    def render(self, context):
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
        ).select_related("campaign")\
        .order_by('?')[0]

        advertising.view()
    except:
        advertising = None

    return {
        'advertising': advertising,
        'site': context.get("site", "")
    }


@register.inclusion_tag('advertising/advertising_group.html', takes_context=True)
def advertising_group(context, dimensions, css_class="rotation-right"):
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
            ).select_related("campaign")\
            .order_by('?')[:nums]

        for ad in list(ads):
            ad.view()
            ads_to_return.append(ad)

    return {
        'ads': ads_to_return,
        'css_class': css_class
    }


def get_event_block_height(tags_count, events_count):
    min_height = 344
    tag_height = 27
    
    if tags_count > 21:
        more_button_height = 52
    else:
        more_button_height = 0

    tags_count = min(tags_count, 21)
    event_height = 84
    two_event_height = 373
    events_count = max(events_count, 2) - 2

    total_tags_height = min_height + tags_count * tag_height + more_button_height
    total_events_height = two_event_height + events_count * event_height

    return max([min_height, total_tags_height, total_events_height])    

@register.inclusion_tag('advertising/advertising_group.html', takes_context=True)
def advertising_home_group(context):
    events_on_page = 9
    tags_count = context["tags"].count()
    request = context['request']

    page = request.GET.get("page", 1)
    eventsFilter = context['eventsFilter']

    if (eventsFilter.qs().count() / events_on_page) < int(page):
        events_count = eventsFilter.qs().count() % events_on_page
    else:
        events_count = events_on_page

    total_height = get_event_block_height(tags_count, events_count)

    print events_count

    print total_height

    heights = OrderedDict([
        (250, ["300x100|300x100", "300x250"]),
        (300, ["300x100|300x100", "300x250"]),
        (350, ["300x250|300x100"]),
        (400, ["300x250|300x100"]),
        (450, ["300x250|300x100|300x100"]),
        (500, ["300x250|300x250", "300x250|300x100|300x100"]),
        (550, ["300x250|300x250", "300x250|300x100|300x100"]),
        (600, ["300x600", "300x250|300x250|300x100"]),
        (650, ["300x600", "300x250|300x250|300x100"]),
        (700, ["300x600|300x100", "300x250|300x250|300x100|300x100"]),
        (750, ["300x600|300x100", "300x250|300x250|300x250", "300x250|300x250|300x100|300x100"]),
        (800, ["300x600|300x100|300x100", "300x250|300x250|300x250"]),
        (850, ["300x600|300x250", "300x250|300x250|300x250|300x100", "300x600|300x100|300x100"]),
        (900, ["300x600|300x250", "300x250|300x250|300x250|300x100", "300x600|300x100|300x100"]),
        (950, ["300x600|300x250|300x100", "300x250|300x250|300x250|300x100|300x100"])
    ])

    for height, dimensions_list in heights.iteritems():
        if total_height > height:
            dimensions = choice(dimensions_list)

    print dimensions

    return advertising_group(context, dimensions=dimensions)

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
def admin_advertising_campaigns(context, campaigns_filter):
    request = context["request"]
    selected_account = context["selected_account"]
    return {
        'campaigns_filter': campaigns_filter,
        'request': request,
        'selected_account': selected_account
    }

@register.inclusion_tag('advertising/stats/advertising-campaign-stats.html', takes_context=True)
def advertising_campaign_stats(context, campaign):
    request = context["request"]
    return {
        'campaign': campaign,
        'request': request
    }    