# -*- coding: utf-8 -*-
from django.contrib.gis.geoip import GeoIP
from django.contrib.gis.geos import Point
from cities.models import City
from event.utils import find_nearest_city
from cities.models import Region


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
        return real_ip.split(',')[0]
    except KeyError:
        return request.META['REMOTE_ADDR']
    except Exception:
        # Unknown IP
        return None


def get_geoip_and_ip(request):
    geoip = GeoIP()
    ip = get_real_ip(request)

    if ip == "127.0.0.1":
        ip = "198.245.113.94"

    return geoip, ip


def get_lon_lat(request):
    if not hasattr(request, '_cached_location'):
        geoip, ip = get_geoip_and_ip(request)

        request._cached_location = geoip.lon_lat(ip)

    return request._cached_location


def get_is_canada(request):
    if not hasattr(request, '_cashed_is_canada'):
        geoip, ip = get_geoip_and_ip(request)

        region_data = geoip.region_by_addr(ip)

        if region_data:
            request._cashed_is_canada = (region_data["country_code"] == "CA")
        else:
            request._cashed_is_canada = False

    return request._cashed_is_canada


def get_user_location(request):
    user_location_type = request.session.get('user_location_type', "city")
    user_location_id = request.session.get('user_location_id', None)

    if "location" in request.GET:
        user_location_type, user_location_id = request.GET["location"].split("|")
        user_location_id = int(user_location_id)

        request.session['user_location_type'] = user_location_type
        request.session['user_location_id'] = user_location_id

    elif not user_location_id:

        location = get_lon_lat(request)

        user_location_type = "city"
        try:
            user_location_id = find_nearest_city(City.objects.all(), Point(location)).id
        except:
            logger.critical("Bad location %s fror point initialization " % location)
            user_location_id = find_nearest_city(City.objects.all(), Point(-106, 54.4)).id

    return {
        "type": user_location_type,
        "id": user_location_id
    }


class LocationMiddleware(object):
    def process_request(self, request):
        request.location = get_lon_lat(request)
        request.is_canada = get_is_canada(request)

        user_location = get_user_location(request)

        request.user_location_type = user_location["type"]
        request.user_location_id = user_location["id"]
