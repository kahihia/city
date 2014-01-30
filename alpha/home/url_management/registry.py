from django.utils.encoding import force_unicode


class UrlManagementRegistry(object):
    def __init__(self):
        self._registry = {}

    def register(self, url_rule):
        self.validate(url_rule)
        name = force_unicode(url_rule.cls_name)
        if name not in self._registry:
            self._registry[name] = url_rule

    @staticmethod
    def validate(url_rule):
        if not hasattr(url_rule, 'get_params'):
            raise Exception(u'Registered url rule must have "get_params" method')

    def __iter__(self):
        return self._registry.itervalues()

url_management_registry = UrlManagementRegistry()