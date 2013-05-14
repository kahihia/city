from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('venue_profile.views',
    url(r'(?P<prof_slug>[-\w]+)/$', 'prprofile', name = 'prprofile'),
)
