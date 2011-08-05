from copy import copy

class TagInfo:
    """
    Pre:
      tag - the tag object, 
      previous_slugs - a list of existing tags in slug form (unicode list) and, 
      num - the number of events which contain that tag
    Post:
      A TagInfo is created with fields:
      status - the class of the tag in the browser instance
      number - the number of events tagged this way
      name - the name of the tag (unicode)
      slug - the slug version of the tag
    """
    def __init__(self, num=0, tag=None, previous_slugs=[]):
        self.number = num
        self.status = u'' #the active field is used for CSS styling        

        if tag:
            self.name = tag.name

            # this code generates the slug of tags to use when
            # this tag is clicked by the user in the browser
            if previous_slugs == []:
                self.slug = tag.slug
            else:
                new_slugs = copy(previous_slugs)
                if tag.slug in previous_slugs: #toggles tag on and off
                    new_slugs.remove(tag.slug) #the new slug wont have our tag when clicked
                    self.status = u'active' #this is used to style the CSS of the tag
                else:
                    new_slugs.append(tag.slug) #the new slug WILL have our tag when clicked
                self.slug = ','.join(new_slugs) #make the new slug by joining with commas (this appears in the URL)
        else:
            self.name = u'All Categories' #this sets up the fake tag, which is a null tag, the absense of tags
            self.slug = ''
            if previous_slugs == []:
                self.status = u'active' #this is used to style the CSS of the tag


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
