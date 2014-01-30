from home.url_management.registry import url_management_registry
import signals
from .urlrules import EventTagsUrlRule

url_management_registry.register(EventTagsUrlRule())