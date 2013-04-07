from models import Venue


def nearest_locations(request):
    venues = Venue.with_active_events.all()
    if request.location:
        venues = venues.distance(request.location).order_by('-distance')[10]

    return {
        "nearest_locations": venues
    }
