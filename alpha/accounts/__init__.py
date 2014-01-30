from home.url_management.registry import url_management_registry
import signals
from venues.urlrules import VanueTypesUrlRule

url_management_registry.register(VanueTypesUrlRule())