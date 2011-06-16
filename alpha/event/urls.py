from django.conf.urls.defaults import patterns, include, url

from alpha.event import views as event
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'edit/(?P<authentication_key>\w+)/$',
                           event.edit
                           name='event_edit'),
                       url(r'view/(?<public_key>\w+)/$',
                           event.view
                           name='event_view'),
)
