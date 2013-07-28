from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings
from accounts.forms import AccountForm

handler404 = 'home.views.custom_404'

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^channel.html$', 'home.views.channelfile'),
    url(r'^finish-setup$', 'home.views.finish_setup'),
    url(r'^nearest-city-and-region$', 'home.views.nearest_city_and_region'),
    url(r'^$', 'event.views.redirect', name='home'),
    url(r'^events/', include('event.urls')),
    url(r'^accounts/', include('userena.urls')),
    url(r'^account-actions/', include('accounts.urls')),
    url(r'^cf-admin/', include('cityfusion_admin.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^advertise/$', 'home.views.redirect', name='advertise'),
    # url(r'^alpha/', include('alpha.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^mamona/', include('mamona.urls')),
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^advertising/', include('advertising.urls')),
    url(r'^accounts/(?P<username>[\.\w-]+)/edit-profile/$',
       'userena.views.profile_edit',
        {
            'edit_profile_form': AccountForm
        },
       name='user_profile_edit',
    ),
    url(r'^account/(?P<username>[\.\w-]+)/$',
       'accounts.views.profile_detail',
       name='account_profile_detail',
    ),

    url(r'^accounts/(?P<username>[\.\w-]+)/edit-profile/(?P<why_message>[\.\w-]+)/(?P<success_url>.*)$',
       'accounts.views.profile_edit',        
       name='user_profile_required',
    ),

    (r'^ckeditor/', include('ckeditor.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (
            r'^static/(?P<path>.*)$',
            'django.views.static.serve',
            {
                'document_root': settings.STATIC_ROOT,
                'show_indexes': True
            }
        ),
   )
    urlpatterns += patterns('',
        (
            r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True
            }
        ),
    )
