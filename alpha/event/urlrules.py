from taggit.models import Tag
from home.url_management.base import BaseUrlRule


class EventTagsUrlRule(BaseUrlRule):
    @classmethod
    def create_url(cls, identifier):
        url = cls.get_stored_url(identifier)
        if not url:
            try:
                tag = Tag.objects.get(name=identifier)
            except Tag.DoesNotExist:
                pass
            else:
                tag_alias = tag.name.replace(' ', '_')
                url = '/%s/' % tag_alias
                cls.store_url(identifier, url)

        return url

    @staticmethod
    def parse_url(path):
        path_components = path.strip('/').split('/')
        # first element is a tag name
        if len(path_components) == 1:
            try:
                tag_name = path_components[0].replace('_', ' ')
                tag = Tag.objects.get(name=tag_name)
            except Tag.DoesNotExist:
                pass
            else:
                callback = 'event.views.browse'
                extra_params = {'tag': tag.name}
                return callback, [], {'extra_params': extra_params}

        return None