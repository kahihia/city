from django import template

register = template.Library()


@register.inclusion_tag('venues/venue_account_item.html', takes_context=True)
def venue_account_item(context, venue_account):
    request = context['request']

    return {
        'request': request,
        'venue_account': venue_account
    }
