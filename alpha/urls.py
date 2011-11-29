from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings

handler404 = 'alpha.home.views.custom_404'

urlpatterns = patterns(
    '',
    # Examples:
    #url(r'^$', 'alpha.home.views.home', name='home'),
    url(r'^channel.html$', 'alpha.home.views.channelfile'),                   
    url(r'^$', 'alpha.event.views.redirect', name='home'),
    url(r'^events/', include('event.urls')),
    url(r'^accounts/', include('citi_user.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^advertise/$', 'alpha.home.views.redirect', name='advertise'),
    # url(r'^alpha/', include('alpha.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 
            'django.views.static.serve', 
            {
                'document_root': settings.MEDIA_ROOT,
            }),
   )
