from django.conf.urls.defaults import patterns, url
from accounts import views as accounts
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^remind-me/(?P<event_id>\d+)/$',
        accounts.remind_me,
        name='remind_me'
    ),
    url(r'^remove-remind-me/(?P<event_id>\d+)/$',
        accounts.remove_remind_me,
        name='remove_remind_me'
    ),
    url(r'^add-in-the-loop/$',
        accounts.add_in_the_loop,
        name='add_in_the_loop'
    ),
    url(r'^reminder-settings/$',
        accounts.reminder_settings,
        name="reminder_settings"
    ),
    url(r'^in-the-loop-settings/$',
        accounts.in_the_loop_settings,
        name="in_the_loop_settings"
    ),
    url(r'^in-the-loop-tags/$',
        accounts.in_the_loop_tags,
        name="in_the_loop_tags"
    ),
    url(r'^remind-email-preview/$', accounts.remind_preview, name="remind_preview"),
    url(r'^in-the-loop-email-preview/$', accounts.in_the_loop_preview),
)
