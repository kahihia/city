from django.conf.urls.defaults import patterns, include, url

from alpha.event import views as event
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', event.browse, name='event_browse'),

                       url(r'edit/(?P<authentication_key>\w+)/$',
                           event.edit,
                           name='event_edit'
                           ),

                       url(r'view/(?P<slug>[^/]+)/',
                           event.view,
                           name='event_view' 
                           ),

                       url(r'create/',
                           event.create,
                           kwargs= { 'send_email': False },
                           name='event_create'
                           ),
)
