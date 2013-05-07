from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('venue_profile.views',
    url(r'', 'prprofile', name = 'prprofile'),
)
