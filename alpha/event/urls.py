from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse

from alpha.event import views as event
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$',
                           event.browse,
                           kwargs={'date': u'flow'},
                           name='event_browse'
                           ),
                       url(r'^edit/(?P<authentication_key>\w+)/$',
                           event.edit,
                           name='event_edit'
                           ),
                       url(r'^view/(?P<slug>[^/]+)/$',
                           event.view,
                           name='event_view' 
                           ),
                       url(r'^create/$',
                           event.create,
                           name='event_create'
                           ),
                       url(r'^create/posted/(?P<slug>[^/]+)/$',
                           event.created,
                           name='event_created'
                           ),
                       url(r'^(?P<old_tags>[^/]+)/$', 
                           event.browse, 
                           name='event_browse_tags'),

                       url(r'^all/(?P<date>[-\w]+)/$', 
                           event.browse, 
                           name='event_browse_date'),

                       url(r'^(?P<old_tags>[^/]+)/(?P<date>[-\w]+)/$', 
                           event.browse, 
                           name='event_browse_tags_date'),

                       url(r'^(?P<old_tags>[^/]+)/(?P<date>[-\w]+)/(?P<num>\d+)/$', 
                           event.browse, 
                           name='event_browse_tags_date_num'),
)
