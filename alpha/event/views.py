from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from event.models import Event
from event.forms import EventFormLoggedIn
from event.forms import EventForm
from taggit.models import Tag

def browse(request):
    #parsing

    #filtering

    #url generation

    #list off all the tags in the system!
    all_tags = Tag.objects.all()
    upcoming_events = Event.events.all()
    return render_to_response('events/browse_events.html',
                              { 'upcoming_events':upcoming_events,
                                'all_tags':all_tags},
                              context_instance = RequestContext(request))

def view(request, slug=None):
    try:
        event = Event.events.get(slug=slug)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_browse'))
    
    return render_to_response('events/event_description.html',
                              {'event': event},
                              context_instance = RequestContext(request))

def create(request, form_class=None, success_url=None,
           template_name='events/create_event.html', send_email=True):
    if form_class == None:
        if request.user.is_authenticated():
            form_class = EventFormLoggedIn
        else:
            form_class = EventForm
    # on success, redirect to the event detail by default
    if success_url is None:
        success_url = reverse('home')
    # Verify and save to the model
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            if not request.user.is_authenticated():
                form.save()
            else:
                event_obj = form.save(commit=False)
                event_obj.owner = request.user
                event_obj = event_obj.save()
                form.save_m2m()
                if send_email:
                    from django.core.email import send_mail
                    current_site = Site.objects.get_current()
                    subject = render_to_string('events/creation_email_subject.txt',
                                               { 'site': current_site,
                                                 'title': event_obj.name })
                    # Email subjects are all on one line
                    subject= ''.join(subject.splitlines())
                    message = render_to_string('events/creation_email.txt',
                                               { 'authentication_key': event_obj.authentication_key,
                                                 'slug': event_obj.slug,
                                                 'site': current_site } )
                    send_mail(subject,message, settings.DEFAULT_FROM_EMAIL, [event_obj.email])
                else:
                    print 'New event edit key: http://127.0.0.1:8000/events/edit/' + event_obj.authentication_key + '/'
                    print 'New event public address: http://127.0.0.1:8000/events/view/' + event_obj.slug + '/'
            if request.user.is_authenticated():
                success_url = reverse('citi_user_events')
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    #Send out the form
    context = RequestContext(request)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)

def edit(request, form_class=None, success_url=None,
         authentication_key=None,
         template_name='events/edit_event.html'):


    if form_class == None:
        if request.user.is_authenticated():
            form_class = EventFormLoggedIn
        else:
            form_class = EventForm

    # Event object is retrieved based on incoming path hash
    # If the hash does not match an existing event, the user
    # is redirected to the event creation page.
    try:
        event_obj = Event.events.get(authentication_key__exact=authentication_key)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_create'))
    if success_url is None:
        success_url = reverse('event_view', kwargs={ 'slug':event_obj.slug})
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
