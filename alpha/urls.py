from django.conf.urls import patterns, include, url
from userena import views as userena_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings
from accounts.forms import AccountForm

handler404 = 'home.views.custom_404'

urlpatterns = patterns(
    '',
    # url(r'^elfinder/', include('elfinder.urls')),
    # Examples:
    url(r'^channel.html$', 'home.views.channelfile'),
    url(r'^facebook-for-turbolinks.js$', 'home.views.facebook_for_turbolinks_js'),
    url(r'^$', 'event.views.browse', name='home'),
    url(r'^events/', include('event.urls')),
    url(r'^venues/', include('venues.urls')),
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
    url(r'^page/(?P<alias>[\.\w-]+)/$', 'home.views.page', name='staticpage'),
    url(r'^notices/', include('notices.urls')),

    url(r'^accounts/signin/$',
       userena_views.signin,
       name='userena_signin'
    ),
    url(r'^accounts/signout/$',
       userena_views.signout,
       name='userena_signout'
    ),
    url(r'^accounts/signup/$',
       userena_views.signup,
       name='userena_signup'
    ),

    url(r'^accounts/(?P<username>[\.\w-]+)/edit/$',
       'accounts.views.profile_edit',
        {
            'edit_profile_form': AccountForm
        },
       name='userena_profile_edit',
    ),
    url(r'^accounts/(?P<username>[\.\w-]+)/$',
       'accounts.views.profile_detail',
       name='userena_profile_detail',
    ),

    url(r'^accounts/(?P<username>[\.\w-]+)/edit-profile/(?P<why_message>[\.\w-]+)/(?P<success_url>.*)$',
       'accounts.views.profile_edit',
       name='user_profile_required',
    ),    

    url(r'^accounts/', include('userena.urls')),

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
