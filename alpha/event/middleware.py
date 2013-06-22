# -*- coding: utf-8 -*-
from django.contrib.gis.geoip import GeoIP
from cities.models import Region


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
        ip = "192.206.151.131"

    return geoip, ip


def get_location(request):
    if not hasattr(request, '_cached_location'):
        geoip, ip = get_geoip_and_ip(request)

        request._cached_location = geoip.lat_lon(ip)

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


def get_canadian_region(request):
    if not hasattr(request, '_cached_canadian_region'):
        geoip, ip = get_geoip_and_ip(request)

        region_data = geoip.region_by_addr(ip)

        if region_data and region_data["country_code"] == "CA":
            code = region_code_table_of_concordance[region_data["region"]]
            request._cached_canadian_region = Region.objects.get(code=code)

        else:
            request._cached_canadian_region = None

    return request._cached_canadian_region


class LocationMiddleware(object):
    def process_request(self, request):
        request.location = get_location(request)
        request.is_canada = get_is_canada(request)
        request.region = get_canadian_region(request)
