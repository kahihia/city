from event.models import Event
from django.db.models import Count, Q
from event.services import location_service

def featured_events_for_region(request):
    region = location_service.LocationForFeaturedEvent(request).canadian_region
    featured_event_query = Q(featuredevent__all_of_canada=True)
    if region:
        featured_event_query = featured_event_query | Q(featuredevent__regions__id=region.id)

    return Event.featured_events\
        .filter(featured_event_query)\
        .order_by('?')\
        .annotate(Count("id"))