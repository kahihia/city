from models import Venue
from django.contrib.gis.geos import Point


def nearest_locations(request):
    venues = Venue.with_active_events()
    if request.location:
        venues = venues.distance(Point(request.location)).order_by('-distance')[:10]

    return {
        "nearest_locations": venues
    }
