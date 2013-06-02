from django.conf.urls.defaults import patterns, url
from advertising import views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^setup/$',
        views.setup,
        name='advertising_setup'
    ),
    url(r'^open/(?P<advertising_id>\d+)/$',
        views.open,
        name='advertising_open'
    )
)
