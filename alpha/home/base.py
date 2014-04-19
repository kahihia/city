class EnhancedObject(object):
    @property
    def cls(self):
        return self.__class__

    @property
    def cls_name(self):
        return self.__class__.__name__


class ModelDecorator(object):
    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, key):
        return getattr(self._instance, key)