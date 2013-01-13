from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse

from feedback.views import feedback, feedback_thanks
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$',
                           feedback,
                           name='feedback'
                           ),
                       url(r'^thanks/$',
                           feedback_thanks,
                           name='feedback_thanks'
                           ),
)
