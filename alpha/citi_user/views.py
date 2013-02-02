from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from event.models import Event
from django.contrib.auth import views as auth_views


def terms(request):
    return render_to_response('registration/terms.html',
                              context_instance = RequestContext(request))

def events(request):
    context = RequestContext(request)
    try:
        user_events = Event.events.filter(owner=request.user)
    except ObjectDoesNotExist:
        pass
    return render_to_response('citi_user/events.html',
                              {'user_events':user_events,
                               'citi_user_events':True},
                              context_instance = context)

def login(request, *args, **kwargs):
    if request.method =='POST':
        if request.POST.get('remember', None):
            request.session.set_expiry(0)
    return auth_views.login(request,*args,**kwargs)
        
