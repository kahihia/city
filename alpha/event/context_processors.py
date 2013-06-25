from cities.models import City, Region


def user_location(request):
    if request.user_location_type == "country":
        user_location_name = "Canada"

    if request.user_location_type == "region":
        region = Region.objects.get(id=request.user_location_id)
        user_location_name = "%s" % (region.name)

    if request.user_location_type == "city":
        city = City.objects.get(id=request.user_location_id)
        user_location_name = "%s, %s" % (city.name, city.region.name)

    return {
        "user_location_id": request.user_location_id,
        "user_location_name": user_location_name
    }
