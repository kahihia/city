from taggit.models import Tag
from home.base import EnhancedObject


class EventTagsUrlRule(EnhancedObject):
    @staticmethod
    def get_params(request):
        path = request.get_full_path()
        path_components = path.strip('/').split('/')
        # first element is a tag name
        if len(path_components) == 1:
            try:
                tag = Tag.objects.get(name=path_components[0])
            except Tag.DoesNotExist:
                pass
            else:
                callback = 'event.views.browse'
                extra_params = {'tag': tag.name}
                return callback, [], {'extra_params': extra_params}

        return None