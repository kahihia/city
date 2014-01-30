class EnhancedObject(object):
    @property
    def cls(self):
        return self.__class__

    @property
    def cls_name(self):
        return self.__class__.__name__