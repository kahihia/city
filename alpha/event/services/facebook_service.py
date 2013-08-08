import datetime
import os
import urllib
import json
from PIL import Image
import dateutil.parser as dateparser
from django.conf import settings
from django.db.models import Q
from django_facebook.api import get_persistent_graph
from event.models import Event, City, FacebookEvent
from taggit.models import Tag


def create_facebook_event(facebook_event_id, related_event):
    facebook_event = FacebookEvent.objects.create(eid=facebook_event_id)
    related_event.facebook_event = facebook_event
    related_event.save()


def get_prepared_event_data(request, data):
    """
    @todo Refactor - split on several methods
    """
    graph = get_persistent_graph(request)
    facebook_event = graph.fql('''select name,
                                         start_time,
                                         end_time,
                                         description,
                                         pic_big,
                                         location,
                                         venue
                                         from event
                                         where eid = %s''' % data['facebook_event_id'])[0]

    if type(facebook_event['start_time']) == int:
        start_time = datetime.datetime.fromtimestamp(facebook_event['start_time'])
    else:
        start_time = dateparser.parse(facebook_event['start_time'])

    if 'end_time' in facebook_event and facebook_event['end_time']:
        if type(facebook_event['end_time']) == int:
            end_time = datetime.datetime.fromtimestamp(facebook_event['end_time'])
        else:
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

    if facebook_event['venue']:
        city = facebook_event['venue'].get('city', '')
        longitude = facebook_event['venue'].get('longitude', '')
        latitude = facebook_event['venue'].get('latitude', '')

    if not facebook_event['venue'] or not (city and longitude and latitude):
        location_data = {param: data[param] for param in ['place', 'geo_venue', 'geo_street',
                                                          'geo_city', 'geo_address', 'geo_country',
                                                          'geo_longtitude', 'geo_latitude', 'street',
                                                          'location_lng', 'location_lat', 'city_0',
                                                          'city_1', 'city_identifier', 'venue_name']}
    else:
        location_data = {
            'place': facebook_event['location'],
            'geo_venue': facebook_event['location'],
            'geo_street': facebook_event['venue'].get('street', ''),
            'geo_city': city,
            'geo_longtitude': longitude,
            'location_lng': longitude,
            'geo_latitude': latitude,
            'location_lat': latitude,
            'venue_name': '',
        }

    result = {
        'name': facebook_event['name'],
        'user_context_type': 'account',
        'user_context_id': request.account.id,
        'family': False,
        'date_night': False,
        'wheelchair': False,
        'website': 'https://www.facebook.com/events/' + data['facebook_event_id'],
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
        'tags': _get_tags_from_description(data['city_id'], facebook_event['description']),
        'picture_src': settings.MEDIA_URL + 'uploads/' + image_basename,
        'cropping': ','.join('%d' % n for n in cropping)
    }

    result.update(location_data)
    return result


def _get_tags_from_description(city_id, description):
    try:
        city = City.objects.get(pk=city_id)
        event_tags = Event.events.filter(venue__city=city).select_related('tags').values('tags')
        tag_ids = set([tag['tags'] for tag in event_tags if tag['tags']])
    except City.DoesNotExist:
        tag_ids = []

    possible_tags = Tag.objects.filter(Q(id__in=tag_ids) |
        Q(name__in=["Free", "Wheelchair"])
    ).values_list('name', flat=True)

    tags = [tag for tag in possible_tags if tag in description]
    return ',' + ','.join(tags) + ','