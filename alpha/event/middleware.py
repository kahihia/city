# -*- coding: utf-8 -*-
from django.utils.functional import SimpleLazyObject
from django.contrib.gis.geoip import GeoIP

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


def get_location(request):
    if not hasattr(request, '_cached_location'):
        g = GeoIP()
        ip = get_real_ip(request)
        ip = "31.43.27.44"
        request._cached_location = g.lat_lon(ip)
    return request._cached_location


class LocationMiddleware(object):
    def process_request(self, request):
        # Don't detect location, until we request it implicitly
        request.location = get_location(request)
