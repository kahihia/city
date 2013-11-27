from accounts.models import VenueAccount, VenueType
from event.services.featured_service import featured_events_for_region
from django.template import RequestContext

from django.shortcuts import render_to_response

def venues(request):
    current_venue_type = int(request.GET.get("venue_type", 0))

    featured_events = featured_events_for_region(request)

    venue_types = VenueType.active_types.all()

    if current_venue_type:
        venue_accounts = VenueAccount.objects.filter(types__id=int(current_venue_type))
    else:
        venue_accounts = VenueAccount.objects.all() # TODO: filter by region

    return render_to_response('venues/index.html', {
        'featured_events': featured_events,
        'venue_accounts': venue_accounts,
        'venue_types': venue_types,
        'current_venue_type': current_venue_type
    }, context_instance=RequestContext(request))