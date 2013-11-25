from accounts.models import VenueAccount
from event.services.featured_service import featured_events_for_region
from django.template import RequestContext

from django.shortcuts import render_to_response

def venues(request):
    featured_events = featured_events_for_region(request)

    venue_accounts = VenueAccount.objects.all() # TODO: filter by region

    return render_to_response('venues/index.html', {
        'featured_events': featured_events,
        'venue_accounts': venue_accounts
    }, context_instance=RequestContext(request))