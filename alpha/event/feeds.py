import urllib

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse

from home.models import Page
from home.utils import shorten_string
from .models import Event, SingleEvent
from .model_decorators import SingleEventModelDecorator


class RssFusionFeed(Rss201rev2Feed):
    extra_elements = ['image', 'date', 'time', 'cost', 'venue', 'location']

    def add_item_elements(self, handler, item):
        super(RssFusionFeed, self).add_item_elements(handler, item)

        for extra_element in self.extra_elements:
            handler.addQuickElement(extra_element, item[extra_element])


class EventFeed(Feed):
    feed_type = RssFusionFeed
    description = 'Last events on Cityfusion'

    def __init__(self):
        self._tag_name = ''
        self._domain = Site.objects.get_current().domain
        self.link = 'http://%s' % self._domain

        try:
            self.title = Page.objects.get(alias='home').meta_title
        except Exception:
            self.title = ''

    def get_object(self, request, *args, **kwargs):
        self._tag_name = request.GET.get('tag', '')
        return super(EventFeed, self).get_object(request, args, kwargs)

    def get_feed(self, obj, request):
        #cache_key = 'rss_feed_%s' % self._tag_name
        #feed = cache.get(cache_key)
        #if not feed:
        feed = super(EventFeed, self).get_feed(obj, request)
        #cache.set(cache_key, feed, 900) # caching for 15 minutes
        return feed

    def items(self):
        if self._tag_name:
            event_ids_with_tags = Event.events.filter(
                tagged_items__tag__name__in=[self._tag_name]
            ).values_list('id', flat=True)
            single_events = SingleEvent.homepage_events.filter(event_id__in=list(event_ids_with_tags))\
                .select_related('event__venue').prefetch_related('event__eventslug_set')
        else:
            single_events = SingleEvent.homepage_events.select_related('event__venue')\
                .prefetch_related('event__eventslug_set').all()
        return [SingleEventModelDecorator(single_event) for single_event in single_events]

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
            u'image': '%s%s' % (self._domain, reverse('get_event_image', kwargs={'slug': item.slug,
                                                                                 'width': 650,
                                                                                 'height': 550})),
            u'date': item.date(),
            u'time': item.time(),
            u'cost': item.price(),
            u'venue': item.venue.name,
            u'location': item.venue.address
        }