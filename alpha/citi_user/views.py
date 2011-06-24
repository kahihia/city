from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from event.models import Event


def terms(request):
    return render_to_response('registration/terms.html',
                              context_instance = RequestContext(request))

def events(request):
    context = RequestContext(request)
    print context
    user_events = Event.events.filter(owner=request.user)
    return render_to_response('citi_user/events.html',
                              {'user_events':user_events},
                              context_instance = context)
