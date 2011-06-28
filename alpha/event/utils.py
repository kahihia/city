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
        
        

