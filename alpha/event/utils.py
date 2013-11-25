import datetime
from cities.models import City
from django.db.models import Count


def find_nearest_city(location, cities=None):
    if not cities:
        cities = City.objects.filter(venue__event__single_events__start_time__gte=datetime.datetime.now()).select_related("region", "region__country").annotate(Count('id'))

    try:
        return cities.distance(location).select_related("region", "region__country").order_by('distance')[0]
    except:
        return None


def get_dates_from_request(request):
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)

    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    else:
        start_date = datetime.datetime.now()

    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    else:
        end_date = datetime.datetime.now()

    return start_date, end_date


def get_times_from_request(request):
    start_time = request.GET.get("start_time", 13)
    end_time = request.GET.get("end_time", 20)
    return start_time, end_time



