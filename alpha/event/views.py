from event.utils import create_key
from event.utils import get_event
from event.utils import generate_form
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


def list(request):
    return render_to_response('events/list_events.html')

def view(request, event_name=None):
    if event_name == None:
        return HttpResponseRedirect(reverse('event'))

def create(request, form_class=None, success_url=None,
           template_name='events/create_event.html'):
    if form_class == None:
        if request.user.is_authenticated():
            form_class = generate_form('owner', 'authentication_key', 'email')
        else:
            form_class = generate_form('owner', 'authentication_key')
    # on success, redirect to the event detail by default
    if success_url is None:
        success_url = reverse('home')
    # Verify and save to the model
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            event_object = form.save(commit=False)
            event_object.authentication_key = create_key()
            event_object.save()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    #Send out the form
    context = RequestContext(request)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)

def edit(request, form_class=None, success_url=None,
         template_name='events/edit_event.html'):
    # Event object is retrieved based on incoming path hash
    # If the hash does not match an existing event, the user
    # is redirected to the event creation page.
    try:
        event_obj = get_event(request.authentication_key)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_create'))
    # Verify and save the form to model
    if request.method == 'POST':
        form = form_class( instance = event_obj,
                              files = request.FILES,
                               data = request.POST )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(instance = event_obj)
    # Edit the event
    context = RequestContext(request)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)
