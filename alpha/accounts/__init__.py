from home.url_management.registry import url_management_registry
import signals
from venues.urlrules import VenueTypesUrlRule

url_management_registry.register(VenueTypesUrlRule())