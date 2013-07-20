# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from event.utils import find_nearest_city
from django.contrib.gis.geos import Point
from cities.models import City
import json

def custom_404(request):
    return render(request,"404.html")

def redirect(request):
    return HttpResponseRedirect(reverse('home'))

# for facebook connect
def channelfile(request):
    return HttpResponse('''<script src="//connect.facebook.net/en_US/all.js"></script>''')

def finish_setup(request):
	request.session['was_setup'] = True
	return HttpResponse(request.session['was_setup'])

def nearest_city_and_region(request):
	location = (
		float(request.GET['latitude']),
		float(request.GET['longitude']),

	)

	nearest_city = find_nearest_city(City.objects.all(), Point(location))

	region_data = {
		"nearest_city_id": nearest_city.id,
		"nearest_city_name": nearest_city.name
	}

	if nearest_city.region:
		region_data["nearest_region_id"] = nearest_city.region.id
		region_data["nearest_region_name"] = nearest_city.region.name

	return HttpResponse(json.dumps(region_data), mimetype="application/json")


