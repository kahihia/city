from django.conf.urls.defaults import patterns, url
from cityfusion_admin import views

urlpatterns = patterns('',
    url(r'^report-event/', 
        views.report_event,
        name='report_event'
    ),
    url(r'^claim-event/',
        views.claim_event_list,
        name='claim_event_list'
    ),

    url(r'^report-event-list/', 
        views.report_event_list,
        name='report_event_list'
    ),
    url(r'^claim-event-list/',
        views.claim_event_list,
        name='claim_event_list'
    ),
)
