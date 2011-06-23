from registration.backends.defaults.urls import urlpatterns

urlpatterns += patterns('',
    url(r'terms/$', 'alpha.citi_user.views.terms', name='citi_user_terms'),
    url(r'events/$', 'alpha.citi_user.views.events', name='citi_user_events'),
)
