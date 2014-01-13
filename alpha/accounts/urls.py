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
        accounts.OrderAdvertisingPdf.as_view(),
        name='account_order_advertising_pdf'
    ),
    url(r'^order-featured-pdf/(?P<order_id>\d+)/$',
        accounts.OrderFeaturedPdf.as_view(),
        name='account_order_featured_pdf'
    ),
    url(r'^set-user-context/(?P<context>[-\w]+)/$',
        accounts.set_context,
        name="account_set_context"
    ),
    url(r'^user-context-profile/$',
        accounts.redirect_to_active_user_context,
        name="user_account_context_page"
    ),
    url(r'^refresh-facebook-graph/$',
        accounts.refresh_facebook_graph,
        name='refresh_facebook_graph'),
    url(r'^accept-transferring/(?P<transferring_id>\d+)/$',
        accounts.accept_transferring,
        name='accept_transferring'),
    url(r'^reject-transferring/(?P<transferring_id>\d+)/$',
        accounts.reject_transferring,
        name='reject_transferring'),
    url(r'^accept-venue-transferring/(?P<venue_transferring_id>\d+)/$',
        accounts.accept_venue_transferring,
        name='accept_venue_transferring'),
    url(r'^reject-venue-transferring/(?P<venue_transferring_id>\d+)/$',
        accounts.reject_venue_transferring,
        name='reject_venue_transferring'),

    url(r'^test-location-determining/$',
        accounts.test_location_determining,
        name='test_location_determining')
)
