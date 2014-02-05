from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree
from xml.dom import minidom

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import reverse

from taggit.models import Tag

from accounts.models import VenueAccount, VenueType
from event.models import SingleEvent
from ..url_management.utils import url_by_identifier


class SiteMap(object):
    SOURCES = ('index', 'page', 'event', 'venue', 'tag', 'venue_type')

    def __init__(self, domain):
        self._domain = domain

    def get_xml(self):
        urlset = Element('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
        for source in self.SOURCES:
            urls = getattr(self, '_get_%s_data' % source)()
            for url_text in urls:
                url = SubElement(urlset, 'url')
                loc = SubElement(url, 'loc')
                loc.text = url_text
                changefreq = SubElement(url, 'changefreq')
                changefreq.text = 'daily'

        return self._prettify(urlset)

    def _get_index_data(self):
        return ['http://%s%s' % (self._domain, reverse('home'))]

    def _get_page_data(self):
        aliases = ['faq', 'advertising', 'privacy_policy', 'terms_of_service']
        return ['http://%s%s' % (self._domain, reverse('staticpage', kwargs={'alias': alias}))
                for alias in aliases]

    def _get_event_data(self):
        single_events = SingleEvent.homepage_events.all()
        return ['http://%s%s' % (self._domain, single_event.get_absolute_url())
                for single_event in single_events]

    def _get_venue_data(self):
        venue_accounts = VenueAccount.public_venues.all()
        return ['http://%s%s' % (self._domain, venue_account.get_absolute_url())
                for venue_account in venue_accounts]

    def _get_tag_data(self):
        tags = Tag.objects.all()
        return ['http://%s%s' % (self._domain, url_by_identifier(tag.name))
                for tag in tags]

    def _get_venue_type_data(self):
        venue_types = VenueType.active_types.all()
        return ['http://%s%s' % (self._domain, url_by_identifier(venue_type.name))
                for venue_type in venue_types]

    def _prettify(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(encoding='utf-8')


def get_sitemap_xml():
    site_map = cache.get('sitemap_xml')
    if not site_map:
        domain = Site.objects.get_current().domain
        site_map = SiteMap(domain).get_xml()
        cache.set('sitemap_xml', site_map, 900) # caching for 15 minutes

    return site_map