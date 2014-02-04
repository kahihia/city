from home.url_management.base import BaseUrlRule
from accounts.models import VenueType


class VenueTypesUrlRule(BaseUrlRule):
    @classmethod
    def create_url(cls, identifier):
        url = cls.get_stored_url(identifier)
        if not url:
            try:
                venue_type = VenueType.active_types.get(name=identifier)
            except VenueType.DoesNotExist:
                pass
            else:
                venue_type_alias = venue_type.name.replace(' & ', '__').replace(' ', '_')
                url = '/%s/' % venue_type_alias
                cls.store_url(identifier, url)

        return url

    @staticmethod
    def parse_url(path):
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