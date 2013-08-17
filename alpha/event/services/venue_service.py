from django.db.models import Q
from cities.models import Country, City
from event.models import Venue
from django.contrib.gis.geos import Point
from event.utils import find_nearest_city


def get_venue_from_request_data(event, data):
    mode = data.get("linking_venue_mode")
    if mode=="SUGGEST":
        return get_venue_suggested_by_user(data)
    if mode=="GOOGLE":
        return get_venue_from_google(data)
    if mode=="OWNER":
        return get_venue_from_owner(event)
    if mode=="EXIST":
        return get_venue_that_exist(data)

def get_venue_suggested_by_user(data):
    name = data.get("venue_name")
    street = data.get("street")
    city = City.objects.get(id=int(data.get("city_identifier")))
    country = Country.objects.get(name='Canada')
    location = Point((
        float(data.get("location_lng")),
        float(data.get("location_lat"))
    ))
    venue = Venue(name=name, street=street, city=city, country=country, location=location, suggested=True)
    venue.save()
    return venue

def get_venue_from_google(data):
    name = data.get("geo_venue")
    street = data.get("geo_street")
    street_number = data.get("geo_street_number")
    city = City.objects.filter(
        Q(name_std=data.get("geo_city").encode('utf8')) |
        Q(name=data.get("geo_city"))
    )
    country = Country.objects.get(name='Canada')
    location = Point((
        float(data.get("geo_longtitude")),
        float(data.get("geo_latitude"))
    ))

    if city.count() > 1:
        city = find_nearest_city(city, location)
    elif not city.count():
        city = City.objects.distance(location).order_by('distance')[0]
    else:
        city = city[0]
    venue, created = Venue.objects.get_or_create(name=name, street=street, city=city, country=country, location=location)

    venue.street_number = street_number
    venue.save()
    return venue


def get_venue_from_owner(event):
    return event.venue_account_owner.venue    

def get_venue_that_exist(data):
    return Venue.objects.get(id=int(data.get("venue_identifier")))