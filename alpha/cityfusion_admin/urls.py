from django.conf.urls.defaults import patterns, url
from cityfusion_admin import views
from django.views.generic import TemplateView

urlpatterns = patterns('',
    # Home
    url(r'^$', 
        TemplateView.as_view(template_name="cf-admin/home.html"),
        name='cfadmin_home'
    ),

    # Reports
    url(r'^report-event/$', 
        views.report_event,
        name='report_event'
    ),
    url(r'^report-event-list/$', 
        views.report_event_list,
        name='report_event_list'
    ),
    url(r'^report-event-process/(?P<report_id>\d+)/$', 
        views.report_event_process,
        name='report_event_process'
    ),

    # Claims
    url(r'^claim-event/$',
        views.claim_event,
        name='claim_event'
    ),    
    url(r'^claim-event-list/$',
        views.claim_event_list,
        name='claim_event_list'
    ),
    url(r'^transfer-event/(?P<claim_id>\d+)/$',
        views.transfer_event,
        name='transfer_event'
    ),
    url(r'^claim-event-refuse/(?P<claim_id>\d+)/$', 
        views.claim_event_refuse,
        name='claim_event_refuse'
    ),

    #Facebook
    url(r'^import-facebook-events/$',
        views.import_facebook_events,
        name='import_facebook_events'
    ),
    url(r'^load-facebook-events/$',
        views.load_facebook_events,
        name='load_facebook_events'
    ),
    url(r'^reject-facebook-event/$',
        views.reject_facebook_event,
        name='reject_facebook_event'
    ),
    url(r'^locations/$',
        views.location_autocomplete,
        name='admin_location_autocomplete'
    ),

    # Advertising
    url(r'^admin-advertising/$',
        views.admin_advertising,
        name='admin_advertising'
    ),
    url(r'^admin-advertising/setup/$',
        views.admin_advertising_setup,
        name='admin_advertising_setup'
    ),    
    url(r'^admin-advertising/campaign/(?P<campaign_id>\d+)/edit/$',
        views.admin_advertising_edit_campaign,
        name='admin_advertising_edit_campaign'
    ),
    url(r'^admin-advertising/campaign/(?P<campaign_id>\d+)/remove/$',
        views.admin_advertising_remove_campaign,
        name='admin_advertising_remove_campaign'
    ),
    url(r'^admin-advertising/ad/(?P<ad_id>\d+)/remove/$',
        views.admin_advertising_remove_ad,
        name='admin_advertising_remove_ad'
    ),
    url(r'^admin-advertising/review/$',
        views.admin_advertising_review,
        name='admin_advertising_review'
    ),
    url(r'^admin-advertising/ad/(?P<ad_id>\d+)/(?P<status>\w+)/$',
        views.admin_advertising_change_status,
        name='admin_advertising_change_status'
    ),


    

    # Features
    url(r'^admin-featured/$',
        views.admin_featured,
        name='admin_featured'
    ),
    url(r'^admin-setup-featured/(?P<event_id>\d+)$',
        views.admin_setup_featured,
        name='admin_setup_featured'
    ),
    url(r'^admin-remove-featured/(?P<featured_event_id>\d+)$',
        views.admin_remove_featured,
        name='admin_remove_featured'
    ),
    url(r'^admin-edit-featured/(?P<featured_event_id>\d+)$',
        views.admin_edit_featured,
        name='admin_edit_featured'
    ),
    url(r'^admin-activate-featured/(?P<featured_event_id>\d+)$',
        views.admin_activate_featured,
        name='admin_activate_featured'
    ),
    url(r'^admin-deactivate-featured/(?P<featured_event_id>\d+)$',
        views.admin_deactivate_featured,
        name='admin_deactivate_featured'
    ),

    url(r'^free-try/$',
        views.free_try,
        name='free_try'
    ),
)
