from django.conf.urls import patterns, url
from . import views as notice

urlpatterns = patterns('',
    url(r'^read-notice/$',
        notice.read_notice,
        name='read_notice'
    ),
)