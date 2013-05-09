from django import template
register = template.Library()
from venue_profile.models import VenueProfile
from accounts.models import Account
from django.shortcuts import get_object_or_404

#@register.simple_tag
#def current_time():
#    return datetime.datetime.now()

@register.inclusion_tag('userena/v_profiles.html', takes_context = True)
def v_profiles(context):
    request = context['request']
    user = request.user
    account = get_object_or_404(Account, user = user)
    venue_profiles = account.venueprofile_set.all()
    return {'venue_profiles':venue_profiles}