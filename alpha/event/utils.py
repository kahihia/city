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

from Event import EVENT_PICTURE_DIR

def picture_file_path(instance = None, filename = None):
    """
    This is used by the model and is defined in the Django
    documentation as a function which is used by the upload_to karg of
    an ImageField I will copy the relevant documentation here from
    FileField.upload_to:
    
    This may also be a callable, such as a function, which will be
    called to obtain the upload path, including the filename. This
    callable must be able to accept two arguments, and return a
    Unix-style path (with forward slashes) to be passed along to the
    storage system. The two arguments that will be passed are:
    
    Argument      Description 

    ------------------------------------------------------------------

    instance      An instance of the model where the
                  FileField is defined. More specifically, this is 
                  the particular instance where the current file is 
                  being attached.
                  
                  In most cases, this object will not have been saved 
                  to the database yet, so if it uses the default 
                  AutoField, it might not yet have a value for its 
                  primary key field.

    filename 	  The filename that was originally given to the
                  file. This may or may not be taken into account 
                  when determining the final destination path.

    Also has one optional argument: FileField.storage, a storage
    object, which handles the storage and retrieval of your files.
    """
    return os.path.join(EVENT_PICTURE_DIR, instance.pk, filename)
