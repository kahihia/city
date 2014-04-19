import logging
import datetime

from django.contrib.gis.geos import Point
from django.contrib.gis.utils.geoip import GeoIP
from django.db.models import Q, Count

from cities.models import City, Region, Country

from event.models import Event, SingleEvent, CountryBorder
from event.utils import find_nearest_city

# Get an instance of a logger
logger = logging.getLogger(__name__)

region_code_table_of_concordance = {
    "AB": "CA.01",
    "BC": "CA.02",
    "MB": "CA.03",
    "NB": "CA.04",
    "NL": "CA.05",
    "NT": "CA.13",
    "NS": "CA.07",
    "NU": "CA.14",
    "ON": "CA.08",
    "PE": "CA.09",
    "QC": "CA.10",
    "SK": "CA.11",
    "YT": "CA.12",
}


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def present_in_session(key, session):
    return key in session and session[key]

def missing_in_session(key, session):
    return not key in session or not session[key]


def get_real_ip(request):
    """
    Get IP from request.

    :param request: A usual request object
    :type request: HttpRequest
    :return: ipv4 string or None
    """
    try:
        # Trying to work with most common proxy headers
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        real_ip = real_ip.split(',')[0]
    except KeyError:
        real_ip = request.META['REMOTE_ADDR']
    except Exception:
        # Unknown IP
        pass
        # real_ip = "198.245.113.94"

    if real_ip == "127.0.0.1":
        real_ip = "198.245.113.94"

    if real_ip.startswith("10.2."):
        logger.warning("Bad ip. Request = %s" % request.META)

    return real_ip


geoip = GeoIP()

class LocationByIP(object):
    def __init__(self, request):
        self.request = request
        self.ip = get_real_ip(request)

    @property
    def country(self):
        code = geoip.country_code(self.ip)
        return get_or_none(Country, code=code)

    @property
    def canadian_region(self):
        region_data = geoip.region_by_addr(self.ip)

        try:
            code = region_code_table_of_concordance[region_data["region"]]
            return get_or_none(Region, country__code="CA", code=code)
        except:
            return None

    @property
    def city(self):
        if self.lat_lon:
            return find_nearest_city(Point(self.lat_lon[::-1]))
        else:
            return None

    @property
    def lat_lon(self):
        return geoip.lat_lon(self.ip)

    @property
    def is_canada(self):
        return geoip.country_code(self.ip)=="CA" or bool(geoip.city(self.ip) and geoip.city(self.ip)["country_code"]=="CA")


class LocationFromBrowser(object):
    def __init__(self, request):
        self.request = request

    @property
    def canadian_region(self):
        if self.lat_lon:
            nearest_city = find_nearest_city(Point(self.lat_lon[::-1]))
            return nearest_city.region
        else:
            return None

    @property
    def city(self):
        if self.lat_lon:
            return find_nearest_city(Point(self.lat_lon[::-1]))
        else:
            return None

    @property
    def lat_lon(self):
        return self.request.session.get("browser_lat_lon", None)

    @lat_lon.setter
    def lat_lon(self, value):
        self.request.session["browser_lat_lon"] = value

    @property
    def is_canada(self):
        if not self.lat_lon:
            return LocationByIP(self.request).is_canada

        pnt = Point(self.lat_lon[::-1])

        countries = CountryBorder.objects.filter(mpoly__contains=pnt)

        for country in countries:
            if country.code=="CA":
                return True

        return False


class LocationFromAccountSettins(object):
    def __init__(self, request):
        self.account = request.account

    @property
    def canadian_region(self):        
        return self.account and self.account.native_region

    @property
    def is_canada(self):
        return not self.account.not_from_canada        

class LocationFromUserChoice(object):
    def __init__(self, request):
        self.request = request
        self.account = request.account
        self.change_user_choice()

        self.by_IP = LocationByIP(request)
        self.from_browser = LocationFromBrowser(request)
        self.from_account_settings = LocationFromAccountSettins(request)

        if self.account and missing_in_session("user_location_data", self.request.session) and self.account.location_type:
            user_location_data = {}
            user_location_data["user_location_id"] = self.account.location_id
            user_location_data["user_location_name"] = self.account.location_name
            user_location_data["user_location_type"] = self.account.location_type

            self.request.session["user_location_data"] = user_location_data


    def change_user_choice(self):
        if 'location' in self.request.GET and self.request.GET['location'].count('|') != 0:
            user_location_data = {}
            user_location_type, user_location_id = self.request.GET['location'].split('|')
            user_location_id = int(user_location_id)

            if user_location_type == 'country':
                user_location_name = 'Canada'

            if user_location_type == 'region':
                region = Region.objects.get(id=user_location_id)
                user_location_name = '%s' % (region.name)

            if user_location_type == 'city':
                city = City.objects.get(id=user_location_id)
                if city.region:
                    user_location_name = '%s, %s' % (city.name, city.region.name)
                else:
                    user_location_name = city.name

            if self.account:
                if self.account.location_type != user_location_type or \
                   self.account.location_name != user_location_name or \
                   self.account.location_id != user_location_id:

                    self.account.location_type = user_location_type
                    self.account.location_name = user_location_name
                    self.account.location_id = user_location_id
                    self.account.save()

            user_location_data['user_location_id'] = user_location_id
            user_location_data['user_location_name'] = user_location_name
            user_location_data['user_location_type'] = user_location_type

            self.request.session['user_location_data'] = user_location_data


    @property
    def city(self):
        if missing_in_session("user_location_data", self.request.session):
            return (self.from_browser.city or self.by_IP.city)

        user_location_data = self.request.session["user_location_data"]

        user_location_id = user_location_data["user_location_id"]
        user_location_type = user_location_data["user_location_type"]

        if user_location_type=="city":
            return City.objects.get(id=user_location_id)
        else:
            return None

    @property
    def canadian_region(self):
        if missing_in_session("user_location_data", self.request.session):            
            return (self.from_account_settings.canadian_region or self.from_browser.canadian_region or self.by_IP.canadian_region)

        user_location_data = self.request.session["user_location_data"]

        user_location_id = user_location_data["user_location_id"]
        user_location_type = user_location_data["user_location_type"]

        return self.region_by_type(user_location_type, user_location_id)


    def region_by_type(self, user_location_type, user_location_id):
        if user_location_type=="country":
            return None
        elif user_location_type=="region":
            return Region.objects.get(id=user_location_id)
        elif user_location_type=="city":
            return City.objects.get(id=user_location_id).region
        return None

    @property
    def location_type(self):
        if not "user_location_data" in self.request.session:
            if not self.from_browser.is_canada:
                return "country"
            if self.city:
                return "city"
            if self.canadian_region:
                return "region"
            return "country"

        return self.request.session["user_location_data"]["user_location_type"]

    @property
    def location_id(self):
        if not "user_location_data" in self.request.session:
            location_type = self.location_type
            if location_type=="city":
                return self.city.id
            if location_type=="region":
                return self.canadian_region.id
            return Country.objects.get(code="CA").id

        return self.request.session["user_location_data"]["user_location_id"]

    @property
    def location_name(self):
        city = self.city
        region = self.canadian_region

        if not "user_location_data" in self.request.session:
            location_type = self.location_type
            if location_type=="city":
                if city.region:
                    return "%s, %s" % (city.name, city.region.name)
                else:
                    return city.name
            if location_type=="region":
                return region.name
            return "Canada"

        return self.request.session["user_location_data"]["user_location_name"]


class LocationForAdvertising(object):
    def __init__(self, request):
        self.request = request

    @property
    def canadian_region(self):
        by_IP = LocationByIP(self.request)
        from_browser = LocationFromBrowser(self.request)
        from_account_settings = LocationFromAccountSettins(self.request)
        from_user_choice = LocationFromUserChoice(self.request)

        return from_user_choice.canadian_region or from_account_settings.canadian_region or from_browser.canadian_region or by_IP.canadian_region


class LocationForFeaturedEvent(LocationForAdvertising):
    pass


def user_location(request):
    by_IP = LocationByIP(request)
    from_browser = LocationFromBrowser(request)
    from_account_settings = LocationFromAccountSettins(request)
    from_user_choice = LocationFromUserChoice(request)

    return {
        "user_location_city": (from_user_choice.city or from_browser.city or by_IP.city),
        "user_location_region": (from_user_choice.canadian_region or from_account_settings.canadian_region or from_browser.canadian_region or by_IP.canadian_region),
        "user_location_lat_lon": by_IP.lat_lon,
        "is_canada": from_browser.is_canada,

        "user_location_type": from_user_choice.location_type,
        "user_location_name": from_user_choice.location_name,
        "user_location_id": from_user_choice.location_id,
        "advertising_region": from_user_choice.canadian_region or from_account_settings.canadian_region or from_browser.canadian_region or by_IP.canadian_region
    }


def get_autocomplete_locations(search, location=None):
    """
        I should give user opportunity to choose region where from events is interesting for him. It can be whole Canada, regions or city
    """
    canada = Country.objects.get(name="Canada")

    locations_with_count, locations_without_count = [], []

    kwargs = {
        "country": canada
    }

    if search:
        kwargs["name__icontains"] = search

    counts, with_count_ids = _get_counts_for_value('venue__city__id')
    cities_with_count = {city.id: city for city in City.objects.filter(**kwargs).filter(id__in=with_count_ids)}
    cities = City.objects.filter(**kwargs).exclude(id__in=with_count_ids)

    if location and location["user_location_lat_lon"]:
        cities = cities.distance(Point(location["user_location_lat_lon"][::-1])).order_by('distance')

    cities_without_count_limit = 5 - len(cities_with_count)
    if cities_without_count_limit > 0:
        cities = cities[0:cities_without_count_limit]
    else:
        cities = []

    for city_id in with_count_ids:
        if city_id in cities_with_count:
            city = cities_with_count[city_id]
            if city.region:
                name = "%s, %s, %s" % (city.name, city.region.name, city.country.name)
            else:
                name = "%s, %s" % (city.name, city.country.name)
            locations_with_count.append({
                "id": city.id,
                "type": "city",
                "name": name,
                "count": counts[city.id]
            })

    for city in cities:
        if city.region:
            name = "%s, %s, %s" % (city.name, city.region.name, city.country.name)
        else:
            name = "%s, %s" % (city.name, city.country.name)
        locations_without_count.append({
            "id": city.id,
            "type": "city",
            "name": name
        })

    counts, with_count_ids = _get_counts_for_value('venue__city__region__id')
    regions_with_count = {region.id: region for region in Region.objects.filter(**kwargs).filter(id__in=with_count_ids)}

    regions_without_count_limit = 3 - len(regions_with_count)
    if regions_without_count_limit > 0:
        regions = Region.objects.filter(**kwargs).exclude(id__in=with_count_ids)[:regions_without_count_limit]
    else:
        regions = []

    for region_id in with_count_ids:
        if region_id in regions_with_count:
            region = regions_with_count[region_id]
            locations_with_count.append({
                "id": region.id,
                "type": "region",
                "name": "%s, %s" % (region.name, region.country.name),
                "count": counts[region.id]
            })

    for region in regions:
        locations_without_count.append({
            "id": region.id,
            "type": "region",
            "name": "%s, %s" % (region.name, region.country.name)
        })

    if not search or search.lower() in "canada":
        canada_count = SingleEvent.homepage_events.count()
        locations_with_count.append({
            "id": canada.id,
            "type": "country",
            "name": "Canada",
            "count": canada_count
        })

    return locations_with_count + locations_without_count


def _get_counts_for_value(value):
    event_counts = list(Event.events.values(value)
                        .annotate(event_count=Count('id'))
                        .filter(Q(single_events__end_time__gte=datetime.datetime.now())
                                &
                                ~Q(Q(single_events__is_occurrence=False) & Q(event_type='MULTIDAY')))
                        .filter(venue__city__isnull=False)
                        .order_by('-event_count')
                        .values_list(value, 'event_count'))

    prepared_counts = {entity: count for (entity, count) in event_counts}
    with_count_ids = [entity for (entity, count) in event_counts]

    return prepared_counts, with_count_ids