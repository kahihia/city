import datetime

from cities.models import City, Region, Country
from event.models import CountryBorder
from event.utils import find_nearest_city
from django.contrib.gis.geos import Point
from django.contrib.gis.utils.geoip import GeoIP

import logging

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

    return real_ip


geoip = GeoIP()

class LocationByIP(object):
    def __init__(self, request):
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
        if "location" in self.request.GET:
            user_location_data = {}
            user_location_type, user_location_id = self.request.GET["location"].split("|")
            user_location_id = int(user_location_id)

            if user_location_type == "country":
                user_location_name = "Canada"

            if user_location_type == "region":
                region = Region.objects.get(id=user_location_id)
                user_location_name = "%s" % (region.name)

            if user_location_type == "city":
                city = City.objects.get(id=user_location_id)
                if city.region:
                    user_location_name = "%s, %s" % (city.name, city.region.name)
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

            user_location_data["user_location_id"] = user_location_id
            user_location_data["user_location_name"] = user_location_name
            user_location_data["user_location_type"] = user_location_type

            self.request.session["user_location_data"] = user_location_data


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
        "user_location_lat_lon": (from_browser.lat_lon or by_IP.lat_lon),
        "is_canada": from_browser.is_canada,

        "user_location_type": from_user_choice.location_type,
        "user_location_name": from_user_choice.location_name,
        "user_location_id": from_user_choice.location_id,
        "advertising_region": from_user_choice.canadian_region or from_account_settings.canadian_region or from_browser.canadian_region or by_IP.canadian_region
    }
