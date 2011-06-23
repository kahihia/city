from django.conf.urls.defaults import patterns, include, url
from registration.urls import urlpatterns

urlpatterns += patterns('',
    url(r'terms/$', 'alpha.citi_user.views.terms', name='citi_user_terms'),
    url(r'events/$', 'alpha.citi_user.views.events', name='citi_user_events'),
)
