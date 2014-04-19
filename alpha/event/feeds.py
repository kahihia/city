import urllib

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from django.conf import settings
from django.core.cache import cache

from home.models import Page
from home.utils import shorten_string
from .models import SingleEvent
from .model_decorators import SingleEventModelDecorator


class RssFusionFeed(Rss201rev2Feed):
    extra_elements = ['image', 'date', 'time', 'price', 'city', 'province', 'venue', 'address', 'tags']

    def add_item_elements(self, handler, item):
        super(RssFusionFeed, self).add_item_elements(handler, item)

        for extra_element in self.extra_elements:
            handler.addQuickElement(extra_element, item[extra_element])


class EventFeed(Feed):
    feed_type = RssFusionFeed
    description = 'Last events on Cityfusion'

    def __init__(self):
        self._domain = Site.objects.get_current().domain
        self.link = 'http://%s' % self._domain

        try:
            self.title = Page.objects.get(alias='home').meta_title
        except Exception:
            self.title = ''

    def get_feed(self, obj, request):
        #feed = cache.get('rss_feed')
        #if not feed:
        feed = super(EventFeed, self).get_feed(obj, request)
        cache.set('rss_feed', feed, 900) # caching for 15 minutes
        return feed

    def items(self):
        return [SingleEventModelDecorator(single_event) for single_event in SingleEvent.homepage_events.all()[:100]]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        mpa = dict.fromkeys(range(32))
        prepared_description = item.event_description().translate(mpa) # removing control characters
        return shorten_string(strip_tags(prepared_description), 500)

    def item_link(self, item):
        return 'http://%s%s' % (self._domain, item.get_absolute_url())

    def item_extra_kwargs(self, item):
        return {
            u'image': 'http://%s%s%s' % (self._domain, settings.MEDIA_URL, urllib.quote(item.image_name)),
            u'date': item.date(),
            u'time': item.time(),
            u'price': item.price(),
            u'city': item.venue.city.name,
            u'province': item.venue.city.region.name,
            u'venue': item.venue.name,
            u'address': item.venue.address,
            u'tags': item.tags_as_string
        }