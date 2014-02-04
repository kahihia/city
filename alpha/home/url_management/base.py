import hashlib
from django.core.cache import cache
from ..base import EnhancedObject

class BaseUrlRule(EnhancedObject):
    @staticmethod
    def get_stored_url(identifier):
        key = hashlib.md5(identifier.encode('utf-8')).hexdigest()
        return cache.get(key)

    @staticmethod
    def store_url(identifier, url):
        key = hashlib.md5(identifier.encode('utf-8')).hexdigest()
        cache.set(key, url, 1800) # caching for 30 minutes

    @staticmethod
    def get_path_components(path):
        path_parts = path.strip('/').split('/')
        return [part for part in path_parts if not part.startswith('?')]