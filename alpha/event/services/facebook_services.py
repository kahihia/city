import datetime
import os
import urllib
import json
from urlparse import urlparse

from django.db.models import Max, Min
from django.utils import timezone
from django.utils.html import strip_tags
from django.conf import settings

from PIL import Image
import dateutil.parser as dateparser
from django_facebook.api import get_persistent_graph

from event.models import Event, FacebookEvent
from ..settings import FACEBOOK_PAGE_ID, EVENTFUL_ID, CONCERTIN_ID


class FacebookImportService(object):
    PAGING_DELTA = 200

    def __init__(self, request, place, page_url):
        """ Create a new facebook import service object.

        @type request: django.core.handlers.wsgi.WSGIRequest
        @type place: str
        @param place: city for search and filter by
        @type page_url: str
        @param page_url: facebook page url (events owner)
        """
        self.request = request
        self.place = place
        self.page_url = page_url

        self.page = 0
        self.graph = get_persistent_graph(request)
        self.lower_place = self.place.lower()

    def get_events_data(self, page):
        """ Get facebook events on the specified page

        @type page: int
        @rtype: dict
        """
        self.page = page
        if self.page_url:
            result = self._get_events_by_page_url()
        else:
            result = self._get_events_by_place()

        return {
            'events': self._filter_data(result['data']),
            'page': (page + 1) if len(result['data']) == self.PAGING_DELTA else 0
        }

    def _get_events_by_place(self):
        params = {
            'q': self.place,
            'type': 'event',
            'fields': 'id,name,owner,description,picture,start_time,end_time,location,venue,ticket_uri',
            'limit': self.PAGING_DELTA
        }

        if self.page:
            params['offset'] = self.page * self.PAGING_DELTA

        return self.graph.get('search', **params)

    def _get_events_by_page_url(self):
        page_identifier = urlparse(self.page_url).path.split('/')[-1]

        params = {
            'fields': 'id,name,owner,description,picture,start_time,end_time,location,venue,ticket_uri',
            'limit': self.PAGING_DELTA
        }

        if self.page:
            params['offset'] = self.page * self.PAGING_DELTA

        return self.graph.get('%s/events' % page_identifier, **params)

    def _filter_data(self, data):
        existing_items = FacebookEvent.objects.all().values_list('eid', flat=True)
        result = []

        for item in data:
            if not int(item['id']) in existing_items \
                    and self._check_place_matching(item) \
                    and not item['owner']['id'] in [EVENTFUL_ID, CONCERTIN_ID]:

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

    def _check_place_matching(self, item):
        """ Check if the item location info complies with the requirements

        @type item: dict
        @rtype: bool
        """
        return not self.lower_place or \
            'location' in item and self.lower_place in item['location'].lower() or \
            'venue' in item and 'city' in item['venue'] and self.lower_place in item['venue']['city'].lower()


def create_facebook_event(event, request):
    graph = get_persistent_graph(request)

    if not graph:
        raise Exception('Error: facebook authentication is required')

    description = '%s\r\n%s' % (strip_tags(event.description),
                  getattr(event, 'comment_for_facebook', ''))

    if event.tickets:
        description = '%s\r\nTickets: %s' % (description, event.tickets)

    location = event.venue.name
    if event.venue.street:
        location += ', %s' % event.venue.street

    location += ', %s' % event.venue.city.name_std
    dates = Event.events.annotate(start_time=Min("single_events__start_time"))\
                 .annotate(end_time=Max("single_events__end_time")).get(pk=event.id)

    if dates.start_time >= dates.end_time:
        raise Exception('Error: The start time must be greater than the end time')

    params = {
        'name': event.name,
        'start_time': dates.start_time.strftime('%Y-%m-%dT%H:%M:%S-0600'),
        'end_time': dates.end_time.strftime('%Y-%m-%dT%H:%M:%S-0600'),
        'description': description,
        'location': location
    }

    user_facebook_id = request.user.get_profile().facebook_id
    if not user_facebook_id:
        user_facebook_info = graph.get('me')
        if user_facebook_info and 'id' in user_facebook_info:
            user_facebook_id = user_facebook_info['id']
        else:
            raise Exception('Error while event posting. Please inform administrator.')

    result = graph.set('%s/events' % user_facebook_id, **params)
    return result['id']


def attach_facebook_event(facebook_event_id, related_event):
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
                                         venue,
                                         ticket_uri
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
        end_time = start_time + datetime.timedelta(hours=3)

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

    city = street = ''
    longitude = latitude = 0

    if facebook_event['venue']:
        city = facebook_event['venue'].get('city', '')
        street = facebook_event['venue'].get('street', '')
        longitude = facebook_event['venue'].get('longitude', 0)
        latitude = facebook_event['venue'].get('latitude', 0)

    if not (city and longitude and latitude):
        city = street = ''
        longitude = latitude = 0

    location_data = {
        'place': facebook_event.get('location', ''),
        'geo_venue': facebook_event.get('location', ''),
        'geo_street': street,
        'geo_street_number': '',
        'geo_city': city,
        'geo_longtitude': longitude,
        'location_lng': longitude,
        'geo_latitude': latitude,
        'location_lat': latitude,
        'venue_name': ''
    }

    description = facebook_event['description'].replace('\n', '<br />\n')

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
        'description': description,
        'description_json': json.dumps({
            'default': description,
            'days': {
                start_time.strftime('%m/%d/%Y'): description
            }
        }),
        'tags': '',
        'tickets': facebook_event['ticket_uri'],
        'picture_src': settings.MEDIA_URL + 'uploads/' + image_basename,
        'cropping': ','.join('%d' % n for n in cropping),
        'linking_venue_mode': 'GOOGLE',
        'event_type': 'SINGLE',
        'occurrences_json': []
    }

    result.update(location_data)
    return result


def _get_time_range_json(start_time, end_time):
    periods = {}
    is_first, is_last = True, False

    while not is_last:
        start = start_time.strftime('%-1I:%M %p') if is_first else '12:00 AM'
        if start_time.strftime('%d%m%Y') != end_time.strftime('%d%m%Y'):
            end = '11:59 PM'
        else:
            end = end_time.strftime('%-1I:%M %p')
            is_last = True

        year = str(start_time.year)
        month = str(start_time.month)
        day = str(start_time.day)

        if not year in periods:
            periods[year] = {}

        if not month in periods[year]:
            periods[year][month] = {}

        if not day in periods[year][month]:
            periods[year][month][day] = {
                'start': start,
                'end': end
            }

        is_first = False
        start_time += datetime.timedelta(days=1)

    return json.dumps(periods)