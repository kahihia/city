from django.conf.urls import *


urlpatterns = patterns('taggit_autosuggest.views',
    url(r'^list/$', 'list_tags', name='taggit_autosuggest-list'),
)
