from django.conf.urls import patterns, url
from accounts import views as accounts
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^remind-me/(?P<single_event_id>\d+)/$',
        accounts.remind_me,
        name='remind_me'
    ),
    url(r'^remove-remind-me/(?P<single_event_id>\d+)/$',
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
    url(r'^cities-autosuggest/$',
        accounts.cities_autosuggest,
        name="cities_autosuggest"
    ),
    url(r'^remind-email-preview/$', accounts.remind_preview, name="remind_preview"),
    url(r'^in-the-loop-email-preview/$', accounts.in_the_loop_preview, name="in_the_loop_preview"),

    url(r'^venue/(?P<slug>[-\w]+)/$',
        accounts.public_venue_account,
        name='public_venue_account'
    ),
    url(r'^venue-private/(?P<slug>[-\w]+)/$',
        accounts.private_venue_account,
        name='private_venue_account'
    ),
    url(r'^venue-edit/(?P<slug>[-\w]+)/$',
        accounts.edit_venue_account,
        name='edit_venue_account'
    ),
    url(r'^venue-create/$',
        accounts.create_venue_account,
        name='create_venue_account'
    ),
    url(r'venue-already-in-use/(?P<venue_account_id>\d+)/$',
        accounts.venue_account_already_in_use,
        name="venue_account_already_in_use"
    ),
    url(r'^set-venue-privacy/(?P<venue_account_id>[\d]+)/(?P<privacy>(public|private))/$',
        accounts.set_venue_privacy,
        name='save_venue_privacy'
    ),
    url(r'^unlink-venue-account/(?P<venue_account_id>[\d]+)/$',
        accounts.unlink_venue_account_from_user_profile,
        name="unlink_venue_account_from_user_profile"
    ),
    url(r'^orders/$',
        accounts.orders,
        name='account_orders'
    ),
    url(r'^order-advertising-printed/(?P<order_id>\d+)/$',
        accounts.order_advertising_printed,
        name='account_order_advertising_printed'
    ),
    url(r'^order-featured-printed/(?P<order_id>\d+)/$',
        accounts.order_featured_printed,
        name='account_order_featured_printed'
    ),
    url(r'^order-advertising-pdf/(?P<order_id>\d+)/$',
        accounts.order_advertising_pdf,
        name='account_order_advertising_pdf'
    ),
    url(r'^order-featured-pdf/(?P<order_id>\d+)/$',
        accounts.order_featured_pdf,
        name='account_order_featured_pdf'
    ),
    url(r'^set-user-context/(?P<context>[-\w]+)/$',
        accounts.set_context,
        name="account_set_context"
    ),
    url(r'^user-context-profile/$',
        accounts.redirect_to_active_user_context,
        name="user_account_context_page"
    )
)
