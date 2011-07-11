from copy import copy

class TagInfo:
    """
    Container for:
    the tag object, 
    a list of existing tags (unicode list) and, 
    the number of events which contain that tag
    """
    def __init__(self, num=0, tag=None, previous_slugs=[]):
        self.number = num

        if tag:
            self.name = tag.name

            if previous_slugs is None:
                self.slug = tag.slug
            else:
                new_slugs = copy(previous_slugs)
                if tag.slug in previous_slugs: #toggles tag on and off
                    new_slugs.remove(tag.slug)
                else:
                    new_slugs.append(tag.slug)
                self.slug = ','.join(new_slugs)
        else:
            self.name = u'All'
            self.slug = ''

from alpha.event.models import Event 
class EventSet:
    """
    EventSets are used by event.views.browse to return a set of events
    and their title. The intention is to allow multiple days to be
    displayed on the browser in one go, if needed.  The way the
    browser was first written, however, only one EventSet is passed to
    the template.

    Container for:
    a name (optional) (unicode string)
    a list of Event objects
    """
    def __init__(self, name=None, events=[]):
        self.name = name
        self.events = events
