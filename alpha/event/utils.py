from django.template.defaultfilters import slugify
from copy import copy
class TagInfo:
    """
    Container for:
    the name of the tag (unicode), 
    a list of existing tags (unicode list) and, 
    the number of events which contain that tag
    """
    def __init__(self, tag, previous_slug, num):
        self.name = tag
        self.number = num
        self.slug = ''

        if previous_slug is None:
            self.slug = slugify(tag)
        elif previous_slug == '':
            self.slug = ''
        else:
            new_slug = copy(previous_slug)
            if tag in previous_slug: #toggles tag on and off
                new_slug.remove(tag)
            else:
                new_slug.append(tag)
            self.slug = ','.join(new_slug)

        

