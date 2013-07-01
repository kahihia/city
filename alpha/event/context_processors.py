from cities.models import City, Region



import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def user_location(request):
    try:
        if request.user_location_type == "country":
            user_location_name = "Canada"

        if request.user_location_type == "region":
            region = Region.objects.get(id=request.user_location_id)
            user_location_name = "%s" % (region.name)

        if request.user_location_type == "city":
            city = City.objects.get(id=request.user_location_id)
            if city.region:            
                user_location_name = "%s, %s" % (city.name, city.region.name)
            else:
                user_location_name = city.name

        return {
            "user_location_id": request.user_location_id,
            "user_location_name": user_location_name
        }

    except:
        logger.critical("def user_location(request): %s, %s " % (request.user_location_id, user_location_name))
        return {
            "user_location_id": 1,
            "user_location_name": "country"

        }
        
