import datetime
import os
import urllib
import json
from PIL import Image
import dateutil.parser as dateparser
from django.conf import settings
from django_facebook.api import get_persistent_graph


def find_nearest_city(cities, location):
    return cities.distance(location).order_by('distance')[0]


def get_dates_from_request(request):
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)

    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    else:
        start_date = datetime.datetime.now()

    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    else:
        end_date = datetime.datetime.now()

    return start_date, end_date


def get_times_from_request(request):
    start_time = request.GET.get("start_time", 13)
    end_time = request.GET.get("end_time", 20)
    return start_time, end_time


def extract_event_data_from_facebook(request, facebook_event_id):
    graph = get_persistent_graph(request)
    facebook_event = graph.fql('''select name,
                                         start_time,
                                         end_time,
                                         description,
                                         pic_big,
                                         location,
                                         venue
                                         from event
                                         where eid = %s''' % facebook_event_id)[0]

    start_time = dateparser.parse(facebook_event['start_time']);
    if 'end_time' in facebook_event and facebook_event['end_time']:
        end_time = dateparser.parse(facebook_event['end_time'])
    else:
        end_time = start_time

    image_basename = os.path.basename(facebook_event['pic_big'])
    image_dist_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'uploads', image_basename))
    urllib.urlretrieve(facebook_event['pic_big'], image_dist_path)

    img = Image.open(image_dist_path)
    img_width, img_height = img.size

    if img_width > img_height:
        bias = int((img_width - img_height) / 2)
        cropping = [bias, 0, bias + img_height, img_height]
    else:
        bias = ((img_height - img_width) / 2)
        cropping = [0, bias, img_width, bias + img_width]

    longitude = facebook_event['venue'].get('longitude', '')
    latitude = facebook_event['venue'].get('latitude', '')

    return {
        'name': facebook_event['name'],
        'user_context_type': 'account',
        'user_context_id': request.account.id,
        'family': False,
        'date_night': False,
        'wheelchair': False,
        'website': 'https://www.facebook.com/events/' + facebook_event_id,
        'when': start_time.strftime('%d-%m-%Y'),
        'when_json': json.dumps({
                        str(start_time.year): {
                            str(start_time.month): {
                                str(start_time.day): {
                                    'start': start_time.strftime('%-1I:%M %p'),
                                    'end': end_time.strftime('%-1I:%M %p')
                                }
                            }
                        }
                    }),
        'description': facebook_event['description'],
        'description_json': json.dumps({
            'default': facebook_event['description'],
            'days': {
                start_time.strftime('%m/%d/%Y'): facebook_event['description']
            }
        }),
        'tags': ',Facebook,',
        'picture_src': settings.MEDIA_URL + 'uploads/' + image_basename,
        'cropping': ','.join('%d' % n for n in cropping),
        'venue_name': '',
        'place': facebook_event['location'],
        'geo_venue': facebook_event['location'],
        'geo_street': facebook_event['venue'].get('street', ''),
        'geo_city': facebook_event['venue'].get('city', ''),
        'geo_longtitude': longitude,
        'location_lng': longitude,
        'geo_latitude': latitude,
        'location_lat': latitude
    }