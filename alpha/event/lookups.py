from selectable.base import ModelLookup
from selectable.registry import registry
from cities.models import City
class CityLookup(ModelLookup):
    model = City
    search_fields = ('name__icontains', )

    # def get_item_label(self, item):
    #     # Display for choice listings
    #     return u"%s, %s" % (item.name, item.region.name)

    def get_item_value(self, item):
        return item.name

    def get_item_id(self, item):
        return "%s,%s" % (item.location.x, item.location.y)

if not 'event-citylookup' in registry._registry:
    registry.register(CityLookup)