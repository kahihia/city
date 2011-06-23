from registration.backends.defaults.urls import urlpatterns

urlpatterns += patterns('',
    url(r'terms/$', 'alpha.citi_user.views.terms', name='terms'),
)
