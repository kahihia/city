from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from event.models import Event
from event.forms import EventFormLoggedIn
from event.forms import EventForm
from event.utils import TagInfo
from event.utils import EventSet

from taggit.models import Tag

from datetime import datetime
from datetime import timedelta

def redirect(request):
    return HttpResponseRedirect( reverse('event_browse'))

def browse(request, old_tags=u'all', date=u'today', num=1):
    split_tags = []
    #parsing the tags string
    if old_tags != u'all':
        split_tags = old_tags.split(',')
        upcoming_events = Event.events.filter(tags__slug__in=split_tags).distinct()
    else:
        upcoming_events = Event.events.all()

    #packaging new tag information given split_tags list
    tags = Tag.objects.all()
    all_tags = []
    all_tags.append( TagInfo(num=Event.events.all().count()) )
    for tag in tags:
        all_tags.append(
            TagInfo(
                tag=tag, #the tag object
                previous_slugs=split_tags, #list of existing tags
                num=Event.events.filter(tags__name__in=[tag]).count() #number of events which are tagged this way
                )
            )

    #now we filter based on the date selected
    today = datetime.now()
    event_sets = []

    if date == u'today':
        todays_events = upcoming_events.filter(start_time__year=today.year, 
                                              start_time__month=today.month,
                                              start_time__day=today.day)
                                              #start_time__hour=today.hour
                                              
        todays_events.order_by('start_time')
        event_sets.append( EventSet(u"Today's Events", todays_events ) )

    if date == u'tomorrow':
        tomorrow = today + timedelta(days=1)
        tomorrows_events = upcoming_events.filter(start_time__year=tomorrow.year, 
                                                 start_time__month=tomorrow.month,
                                                 start_time__day=tomorrow.day)
        tomorrows_events.order_by('start_time')
        event_sets.append( EventSet(u"Tomorrow's Events", tomorrows_events ) )

    if date == u'this-weekend':
        #weekday 6 5 4 sun sat fri
        end = today + timedelta(days=6-today.weekday())
        end = end.replace(hour=23,minute=59,second=59,microsecond=0)
        #sat is 5
        if today.weekday() == 5:
            start = today + timedelta(days=5-today.weekday())
            start = start.replace(hour=0,minute=0,second=0,microsecond=0)
        #friday at 5pm is the weekend.
        else:
            start = today + timedelta(days=4-today.weekday())
            start = start.replace(hour=17,minute=0,second=0,microsecond=0)
        this_weekends_events = upcoming_events.filter(start_time__range=(start,end))
        this_weekends_events.order_by('start_time')
        event_sets.append( EventSet(u"Event's This Weekend", this_weekends_events) )
    if date == u'next-weekend':
        next_monday = today + timedelta(days=7-today.weekday())
        end = next_monday + timedelta(days=6-next_monday.weekday())
        start = next_monday + timedelta(days=4-next_monday.weekday())
        next_weekends_events = upcoming_events.filter(start_time__range=(start,end))
        next_weekends_events.order_by('start_time')
        event_sets.append( EventSet(u"Event's Next Weekend", next_weekends_events) )
    if date == u'this-week':
        end = today + timedelta(days=6-today.weekday())
        start = today
        this_weeks_events = upcoming_events.filter(start_time__range=(start,end))
        this_weeks_events.order_by('start_date')
        event_sets.append( EventSet(u"Event's This Week" ) )
    if date == u'next-week':
        end = today + timedelta(days=13-today.weekday())
        start = today + timedelta(days=7-today.weekday())
        next_weeks_events = upcoming_events.filter(start_time__range=(start,end))
        next_weeks_events.order_by('start_date')
        event_sets.append( EventSet(u"Event's Next Week") )    


    # error checking for num argument
    if num < 1:
        num = 1


    return render_to_response('events/browse_events.html',
                              { 'upcoming_events':upcoming_events,
                                'all_tags':all_tags,
                                'current_tags':old_tags,
                                'page_date':date,
                                'page_num':num,
                                'event_sets':event_sets},
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
