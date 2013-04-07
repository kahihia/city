from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.defaults import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from registration.views import activate
from registration.views import register

from citi_user.forms import CityAuthForm
from citi_user.forms import CityRegistrationForm
from citi_user.views import login
urlpatterns = patterns(
    '',
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.

    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
        name='registration_activate'),

    url(r'terms/$', 'citi_user.views.terms', name='citi_user_terms'),
    url(r'events/$', 'citi_user.views.events', name='citi_user_events'),
    )
