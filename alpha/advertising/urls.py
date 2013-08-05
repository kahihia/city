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
    ),
    url(r'^payment/(?P<order_id>\d+)/$',
        views.payment,
        name='advertising_payment'
    ),
    url(r'^campaign/(?P<campaign_id>\d+)/edit/$',
        views.edit_campaign,
        name='advertising_edit_campaign'
    ),
    url(r'^campaign/(?P<campaign_id>\d+)/remove/$',
        views.remove_campaign,
        name='advertising_remove_campaign'
    ),
    url(r'^campaign/(?P<campaign_id>\d+)/deposit/$',
        views.deposit_funds_for_campaign,
        name='advertising_deposit_funds_for_campaign'
    ),
    url(r'^advertising-order/(?P<order_id>\d+)/$',
        views.advertising_order,
        name='advertising_order'
    ),
)
