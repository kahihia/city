import datetime
import os
import urllib
import json
from PIL import Image
import dateutil.parser as dateparser
from django.conf import settings
from django.db.models import Max, Min
from django.utils import timezone
from django.utils.html import strip_tags
from django_facebook.api import get_persistent_graph
from event.models import Event, FacebookEvent
from ..settings import FACEBOOK_PAGE_ID


def get_facebook_events_data(request, place, page):
    paging_delta = 200

    fb = get_persistent_graph(request)
    params = {
        'q': place,
        'type': 'event',
        'fields': 'id,name,description,picture,start_time,end_time,location,venue,ticket_uri',
        'limit': paging_delta
    }

    if page:
        params['offset'] = page * paging_delta

    result = fb.get('search', **params)
    events = _get_filtered_events(result['data'], place.lower())

    return {
        'events': events,
        'page': (page + 1) if len(result['data']) == paging_delta else 0
    };


def create_facebook_event(facebook_event_id, related_event, request=None):
    if not facebook_event_id and request:
        facebook_event_id = int(_create_external_facebook_event(related_event, request))

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
        'when_json': _get_time_range_json(start_time, end_time),
        'description': facebook_event['description'],
        'description_json': json.dumps({
            'default': facebook_event['description'],
            'days': {
                start_time.strftime('%m/%d/%Y'): facebook_event['description']
            }
        }),
        'tags': data['tags'],
        'tickets': data['tickets'],
        'picture_src': settings.MEDIA_URL + 'uploads/' + image_basename,
        'cropping': ','.join('%d' % n for n in cropping)
    }

    result.update(location_data)
    return result


def _create_external_facebook_event(event, request):
    fb = get_persistent_graph(request)
    description = '%s\r\n%s' % (strip_tags(event.description), 
        getattr(event, 'comment_for_facebook', ''))

    location = event.venue.name
    if event.venue.street:
        location += ', %s' % event.venue.street

    location += ', %s' % event.venue.city.name_std
    dates = Event.events.annotate(start_time=Min("single_events__start_time"))\
                .annotate(end_time=Max("single_events__end_time")).get(pk=event.id)

    params = {
        'name': event.name,
        'start_time': dates.start_time.strftime('%Y-%m-%dT%H:%M:%S+0000'),
        'end_time': dates.end_time.strftime('%Y-%m-%dT%H:%M:%S+0000'),
        'description': description,
        'location': location,
        'ticket_uri': event.tickets
    }

    result = fb.set('%s/events' % FACEBOOK_PAGE_ID, **params)
    return result['id']


def _get_time_range_json(start_time, end_time):
    periods = {}
    is_first, is_last = True, False

    while start_time <= end_time and not is_last:
        prev_time = start_time
        start_time += datetime.timedelta(days=1)
        if start_time < end_time:
            added_time = prev_time
        else:
            added_time = end_time
            is_last = True

        year = str(added_time.year)
        month = str(added_time.month)
        day = str(added_time.day)

        if not year in periods:
            periods[year] = {}

        if not month in periods[year]:
            periods[year][month] = {}

        if not day in periods[year][month]:
            periods[year][month][day] = {
                'start': added_time.strftime('%-1I:%M %p') if is_first else '12:00 AM',
                'end': added_time.strftime('%-1I:%M %p') if is_last else '11:59 PM'
            }

        is_first = False

    return json.dumps(periods)


def _get_filtered_events(raw_data, city_name):
    existing_items = FacebookEvent.objects.all().values_list('eid', flat=True)
    result = []

    for item in raw_data:
        if not int(item['id']) in existing_items \
                and 'location' in item \
                and city_name in item['location'].lower():

            for key in ['start_time', 'end_time']:
                if key in item:
                    item[key] = dateparser.parse(item[key])
                else:
                    item[key] = None

                if item[key] and not timezone.is_aware(item[key]):
                    item[key] = item[key].replace(tzinfo=timezone.utc)

            time_now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
            if item['start_time'] > time_now \
                    or (item['end_time'] and item['end_time'] > time_now):
                item['picture'] = item['picture']['data']['url']
                result.append(item)

    return result