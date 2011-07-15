from django.conf.urls.defaults import patterns, include, url

from alpha.event import views as event
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$',
                           {'date': u'flow'},
                           event.browse
                           name='event_flow'
                           ),
                       url(r'^all/today/$', event.browse, name='event_browse'),
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
