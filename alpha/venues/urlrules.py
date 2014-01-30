from home.base import EnhancedObject
from accounts.models import VenueType


class VenueTypesUrlRule(EnhancedObject):
    @staticmethod
    def get_params(request):
        path = request.get_full_path()
        path_components = path.strip('/').split('/')
        # first element is a venue type name
        if len(path_components) == 1:
            try:
                venue_type_name = path_components[0].replace('__', ' & ').replace('_', ' ')
                venue_type = VenueType.active_types.get(name=venue_type_name)
            except VenueType.DoesNotExist:
                pass
            else:
                callback = 'venues.views.venues'
                extra_params = {'venue_type': venue_type.name}
                return callback, [], {'extra_params': extra_params}

        return None