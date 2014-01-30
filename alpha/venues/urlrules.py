from home.base import EnhancedObject
from accounts.models import VenueType


class VanueTypesUrlRule(EnhancedObject):
    @staticmethod
    def get_params(request):
        path = request.get_full_path()
        path_components = path.strip('/').split('/')
        # first element is a venue type name
        if len(path_components) == 1:
            try:
                venue_type = VenueType.active_types.get(name=path_components[0])
            except VenueType.DoesNotExist:
                pass
            else:
                callback = 'venues.views.venues'
                extra_params = {'venue_type': venue_type.name}
                return callback, [], {'extra_params': extra_params}

        return None