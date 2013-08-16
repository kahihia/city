from django import template
register = template.Library()
from accounts.models import Account
from django.shortcuts import get_object_or_404


@register.inclusion_tag('userena/venue_accounts.html', takes_context=True)
def venue_accounts(context):
    request = context['request']
    user = request.user
    account = get_object_or_404(Account, user=user)
    venue_accounts = account.venueaccount_set.all()

    return {
        'venue_accounts': venue_accounts
    }
