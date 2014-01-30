from django.core.urlresolvers import get_callable
from .registry import url_management_registry


class UrlManagementMiddleware(object):
    def process_request(self, request):
        for url_rule in url_management_registry:
            params = url_rule.get_params(request)
            if params:
                callback, callback_args, callback_kwargs = params
                if not callable(callback):
                    callback = get_callable(callback)
                return callback(request, *callback_args, **callback_kwargs)
        return None