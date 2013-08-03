from cities.models import City, Region
from ipaddresslab import IPAdressLab
from event.utils import find_nearest_city
from django.contrib.gis.geos import Point

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

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
        real_ip = "198.245.113.94"

    if real_ip == "127.0.0.1":
        real_ip = "10.2.46.128"

    return real_ip


class LocationMiddleware(object):
    def process_request(self, request):
        user_location_data = request.session.get('user_location_data', False)
        if not user_location_data:
            user_location_data = {}

            ip = get_real_ip(request)
            ipinfo = IPAdressLab(ip=ip)
            location = ipinfo.lon_lat()

            user_location_type = "city"
            nearest_city = find_nearest_city(City.objects.all(), Point(location))
            user_location_id = find_nearest_city(City.objects.all(), Point(location)).id

            user_location_data["location"] = location
            user_location_data["user_location_id"] = nearest_city.id

            if nearest_city.region:
                user_location_data["user_location_name"] = "%s, %s" % (nearest_city.name, nearest_city.region.name)
            else:
                user_location_data["user_location_name"] = nearest_city.name

            user_location_data["user_location_type"] = "city"
            user_location_data["nearest_city"] = nearest_city
            if nearest_city.region:
                user_location_data["nearest_region"] = nearest_city.region

            user_location_data["user_location_type"] = "country"
            user_location_data["user_location_name"] = "Canada"
            user_location_data["user_location_id"] = 6251999

        if "location" in request.GET:
            user_location_type, user_location_id = request.GET["location"].split("|")
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

            user_location_data["user_location_id"] = user_location_id
            user_location_data["user_location_name"] = user_location_name
            user_location_data["user_location_type"] = user_location_type



        request.session["user_location_data"] = user_location_data

        request.user_location = user_location_data            

        # except:
        #     logger.critical("def user_location(request): %s " % (request.user_location_id))
        #     request.user_location = {
        #         "user_location_id": 1,
        #         "user_location_name": "Canada",
        #         "location": (-106.6667, 52.1333)
        #     }

class SetupMiddleware(object):
    def process_request(self, request):
        request.was_setup = request.session.get('was_setup', False)
