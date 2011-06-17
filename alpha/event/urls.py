from django.conf.urls.defaults import patterns, include, url

from alpha.event import views as event
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       #url(r'^$', event.list, name='event'),

                       #url(r'edit/(?P<authentication_key>\w+)/$',
                       #    event.edit,
                       #    name='event_edit'),

                       #url(r'view/(?<event_name>\w+)/$',
                       #    event.view,
                       #    name='event_view'),
                       url(r'create/',
                           event.create,
                           name='event_create'),
)
