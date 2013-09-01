from django.conf.urls import *
from utils import import_backend_modules

includes_list = []
for bknd_name, urls in import_backend_modules('urls').items():
	includes_list.append(url(r'^%s/' % bknd_name, include(urls)))

urlpatterns = patterns('mamona',
		url('^order/$', 'views.process_order', name='mamona-process-order'),
		url('^payment/(?P<payment_id>[0-9]+)/(?P<order_class>[^/]+)/$', 'views.process_payment', name='mamona-process-payment'),
		url('^confirm/(?P<payment_id>[0-9]+)/(?P<order_class>[^/]+)/$', 'views.confirm_payment', name='mamona-confirm-payment'),
		*includes_list
		)
