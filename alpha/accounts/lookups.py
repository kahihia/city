from selectable.base import ModelLookup
from selectable.registry import registry
from cities.models import Region


class RegionLookup(ModelLookup):
    model = Region
    search_fields = ('name__icontains', )
    filters = {'country__code': "CA", }    

    def get_item_value(self, item):
        return item.name

    def get_item_id(self, item):
        return item.id

if not 'event-regionlookup' in registry._registry:
    registry.register(RegionLookup)
