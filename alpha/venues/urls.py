from django.conf.urls import patterns, url
from venues import views

urlpatterns = patterns('',
    url(r'^$',
        views.venues,
        name='venues'
    )
)
