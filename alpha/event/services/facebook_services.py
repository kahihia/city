import datetime
import os
import urllib
import urllib2
import json
from urlparse import urlparse
from HTMLParser import HTMLParser

from django.db.models import Max, Min
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings

from PIL import Image
import dateutil.parser as dateparser
from django_facebook.api import get_persistent_graph
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from event.models import Event, FacebookEvent, SingleEvent
from ..settings import EVENTFUL_ID, CONCERTIN_ID


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


def create_facebook_event(event, request, facebook_owner_id, facebook_owner_type='user'):
    graph = get_persistent_graph(request)

    if not graph:
        raise Exception('Error: facebook authentication is required')

    parser = HTMLParser()
    description = strip_tags(parser.unescape(event.description))

    googlemap_link = 'http://maps.google.com/?ie=UTF8&hq=&q=%s,%s&ll=%s,%s&z=13' % (event.location.y, event.location.x,
                                                                                    event.location.y, event.location.x)
    description = '%s\r\n\nLocation: %s\r\n\nPrice: %s' % (description, googlemap_link, event.price)

    if facebook_owner_type == 'user' and event.tickets:
        description = '%s\r\n\nTickets: %s' % (description, event.tickets)

    location = event.venue.name
    if event.venue.street:
        location += ', %s' % event.venue.street

    location += ', %s' % event.venue.city.name_std
    dates = Event.events.annotate(start_time=Min('single_events__start_time'))\
                 .annotate(end_time=Max('single_events__end_time')).get(pk=event.id)

    if dates.start_time >= dates.end_time:
        dates.end_time += datetime.timedelta(days=1)

    common_params = {
        'name': event.name,
        'description': unicode(description).encode('utf-8'),
        'location': location
    }

    if facebook_owner_type == 'page' and event.tickets:
        validate = URLValidator()
        try:
            validate(event.tickets)
            common_params['ticket_uri'] = event.tickets
        except ValidationError:
            pass

    if event.is_multiday():
        single_events = list(SingleEvent.homepage_events.filter(event=event))
    else:
        single_events = list(SingleEvent.future_events.filter(event=event))

    event_url = '%s/events' % facebook_owner_id
    event_images = list(event.sorted_images)
    have_images = False
    if len(event_images) > 0:
        event_image = os.path.abspath(os.path.join(settings.MEDIA_ROOT, event_images[0].picture.path))
        have_images = True

    event_groups, event_group = [], []
    index = 0
    for single_event in single_events:
        event_group.append(single_event)
        index += 1
        if index == 10:
            event_groups.append(event_group)
            index, event_group = 0, []

    if index != 0:
        event_groups.append(event_group)

    facebook_event_ids, posted_single_events = [], []
    for event_group in event_groups:
        batch, attached_images = [], {}
        for single_event in event_group:
            if not single_event.facebook_event:
                posted_single_events.append(single_event)
                params = common_params.copy()
                params.update({
                    'start_time': single_event.start_time.strftime('%Y-%m-%dT%H:%M:%S-0600'),
                    'end_time': single_event.end_time.strftime('%Y-%m-%dT%H:%M:%S-0600'),
                })

                operation_name = 'create-event-%s' % single_event.id

                batch.append({
                    'method': 'POST',
                    'relative_url': event_url,
                    'body': urllib.urlencode(params),
                    'name': operation_name,
                    'omit_response_on_success': False
                })

                if have_images:
                    picture_url = '{result=%s:$.id}/picture' % operation_name
                    image_name = 'source%s' % single_event.id

                    batch.append({
                        'method': 'POST',
                        'relative_url': picture_url,
                        'attached_files': image_name
                    })

                    attached_images[image_name] = open(event_image)

        if posted_single_events:
            values = {
                'access_token': graph.access_token,
                'batch': json.dumps(batch)
            }

            if have_images:
                values.update(attached_images)

            response = _send_multipart_data(graph.api_url, values)
            for item in response:
                data = json.loads(item['body'])
                if type(data) == dict and 'id' in data:
                    facebook_event_ids.append(data['id'])

    if not posted_single_events:
        raise Exception('Error: no events for posting')

    result = {}
    for i in range(0, len(posted_single_events)):
        attach_facebook_event(int(facebook_event_ids[i]), posted_single_events[i])
        result[posted_single_events[i].id] = facebook_event_ids[i]

    if event.is_multiday():
        single_event = SingleEvent.objects.filter(event=event, is_occurrence=False)[0]
        single_event.facebook_event = posted_single_events[0].facebook_event
        single_event.save()

    return result


def attach_facebook_event(facebook_event_id, related_event):
    facebook_event = save_facebook_event(facebook_event_id)
    related_event.facebook_event = facebook_event
    related_event.save()


def save_facebook_event(facebook_event_id):
    return FacebookEvent.objects.create(eid=facebook_event_id)


def get_facebook_user_id(request):
    graph = get_persistent_graph(request)
    user_facebook_info = graph.get('me')

    if user_facebook_info and 'id' in user_facebook_info:
        return user_facebook_info['id']
    else:
        raise Exception('Error while getting user facebook id. Please inform administrator.')


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
                                         pic_cover,
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

    image_source = facebook_event['pic_cover']['source'] if facebook_event['pic_cover'] \
        and 'source' in facebook_event['pic_cover'] \
        else facebook_event['pic_big']

    location = city = street = ''
    longitude = latitude = 0

    if facebook_event['venue']:
        location = facebook_event.get('location', '')
        city = facebook_event['venue'].get('city', '')
        street = facebook_event['venue'].get('street', '')
        longitude = facebook_event['venue'].get('longitude', 0)
        latitude = facebook_event['venue'].get('latitude', 0)

    if not (city and longitude and latitude):
        location = city = street = ''
        longitude = latitude = 0

    location_data = {
        'place': location,
        'geo_venue': location,
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
        'price': '$',
        'description': description,
        'description_json': json.dumps({
            'default': description,
            'days': {
                start_time.strftime('%m/%d/%Y'): description
            }
        }),
        'tags': '',
        'tickets': facebook_event['ticket_uri'],
        'images': _get_images_json(image_source),
        'picture_src': '',
        'cropping': '',
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
            delta = datetime.date(end_time.year, end_time.month, end_time.day)\
                    - datetime.date(start_time.year, start_time.month, start_time.day)
            if is_first and delta.days == 1:
                end = end_time.strftime('%-1I:%M %p')
                is_last = True
            else:
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


def _get_images_json(image_source):
    image_basename = os.path.basename(image_source)
    image_dist_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'uploads', image_basename))
    urllib.urlretrieve(image_source, image_dist_path)

    img = Image.open(image_dist_path)
    img_width, img_height = img.size

    if img_width > img_height:
        bias = int((img_width - img_height) / 2)
        cropping = [bias, 0, bias + img_height, img_height]
    else:
        bias = ((img_height - img_width) / 2)
        cropping = [0, bias, img_width, bias + img_width]

    images_data = {
        'images': [{
            'filepath': settings.MEDIA_URL + 'uploads/' + image_basename,
            'cropping': ','.join('%d' % n for n in cropping)
        }]
    }

    return json.dumps(images_data)


def _send_multipart_data(url, values):
    """ Generate and send multipart data

    @type url: str
    @type values: dict
    @rtype: list
    """
    register_openers()
    data, headers = multipart_encode(values)
    headers['User-agent'] = 'Open Facebook Python'
    request = urllib2.Request(url, data, headers)
    request.unverifiable = True
    response = urllib2.urlopen(request)

    return json.loads(response.read())