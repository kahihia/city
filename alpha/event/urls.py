from django.conf.urls import patterns, include, url
from event import views as event
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',
        event.browse,
        name='event_browse'
    ),
    url(r'^search/$',
        event.search_pad,
        name='search_pad'
    ),
    url(r'^edit/(?P<authentication_key>\w+)/$',
        event.edit,
        name='event_edit'
    ),
    url(r'^copy/(?P<authentication_key>\w+)/$',
        event.copy,
        name='event_copy'
    ),
    url(r'^remove/(?P<authentication_key>\w+)/$',
        event.remove,
        name='event_remove'
    ),
    url(r'^setup_featured/(?P<authentication_key>\w+)/$',
        event.setup_featured,
        name='event_setup_featured'
    ),
    url(r'^view/(?P<slug>[^/]+)/$',
        event.view,
        name='event_view'
    ),
    url(r'^view/(?P<slug>[^/]+)/(?P<date>[-\w]+)/$',
        event.view,
        name='event_view'
    ),

    url(r'^view-featured/(?P<slug>[^/]+)/(?P<date>[-\w]+)/$',
        event.view_featured,
        name='event_view_featured'
    ),
    url(r'^view/(?P<slug>[^/]+)/(?P<old_tags>[^/]+)/$',
        event.view,
        name='event_view_tags'
    ),
    url(r'^create/tags/$', event.ason),
    url(r'^create/$',
        event.create,
        name='event_create'
    ),
    url(r'^create-from-facebook/$',
        event.create_from_facebook,
        name='event_create_from_facebook'
    ),

    url(r'^start$', event.start, name="start"),
    url(r'^ajax-upload$', event.import_uploader, name="my_ajax_upload"),
    url(r'^city_tags$', event.city_tags, name='city_tags'),
    url(r'^create/posted/(?P<slug>[^/]+)/$',
        event.created,
        name='event_created'
    ),
    url(r'^save-active-tab/(?P<page>[^/]+)/(?P<tab>[^/]+)/$', event.save_active_tab, name="save_active_tab"),
    url(r'^audit-event/$', event.audit_event_list, name="audit_event_list"),
    url(r'^audit-event-remove/(?P<id>\d+)/$', event.audit_event_remove, name="audit_event_remove"),
    url(r'^audit-event-edit/(?P<id>\d+)/$', event.audit_event_edit, name="audit_event_edit"),
    url(r'^audit-event-update/(?P<id>\d+)/$', event.audit_event_update, name="audit_event_update"),
    url(r'^audit-event-admin-update/(?P<id>\d+)/$', event.audit_event_admin_update, name="audit_event_admin_update"),
    url(r'^audit-event-approve/(?P<id>\d+)/$', event.audit_event_approve, name="audit_event_approve"),
    url(r'^nearest_venues/$', event.nearest_venues, name='nearest_venues'),
    url(r'^locations/$', event.location_autocomplete, name="location_autocomplete"),
    url(r'^payment/(?P<order_id>\d+)/$',
        event.payment,
        name='setup_featured_payment'
    ),
    url(r'^featured-event-order/(?P<order_id>\d+)/$',
        event.featured_event_order,
        name='featured_event_order'
    ),

    url(r'^suggest-cityfusion-venue/$',
        event.suggest_cityfusion_venue,
        name="suggest_cityfusion_venue"
    ),

    url(r'^set-browser-location/$',
        event.set_browser_location,
        name="set_browser_location"
    ),

    # url(r'^audit-single-event/', event.audit_single_event_list),
    # url(r'^audit-single-remove/(?P<id>\d+)', event.audit_single_event_remove),
    # url(r'^audit-single-edit/(?P<id>\d+)', event.audit_single_event_edit),
    # url(r'^audit-single-event-update/(?P<id>\d+)', event.audit_single_event_update),


    url(r'^(?P<old_tags>[^/]+)/$',
        event.browse,
        name='event_browse_tags'
    ),
    url(r'^all/(?P<date>[-\w]+)/$',
        event.browse,
        name='event_browse_date'),
    url(r'^(?P<old_tags>[^/]+)/(?P<date>[-\w]+)/$',
        event.browse,
        name='event_browse_tags_date'),

    url(r'^(?P<old_tags>[^/]+)/(?P<num>\d+)/$',
        event.browse,
        name='event_browse_tags_num'),

    url(r'^(?P<old_tags>[^/]+)/(?P<date>[-\w]+)/(?P<num>\d+)/$',
        event.browse,
        name='event_browse_tags_date_num'),

    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
)
