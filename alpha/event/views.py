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

from django.conf import settings

import re

def redirect(request):
    return HttpResponseRedirect( reverse('event_browse'))

def browse(request, old_tags=u'all', date=u'today', num=1):
    pages = False # used in date filter code for determining if we have pagination
    num = int(num) -1 # see comment labeled NUMCODE

    split_tags = []
    #parsing the tags string
    if old_tags != u'all':
        split_tags = old_tags.split(',')
        # Right now we query based on tags, and then later split this up based on date.
        # Does django make a query every time? If so this could be an expensive, inefficient way of
        # doing the job.
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
    # Sam note: I realize that i have way too many queries here, but im not really sure how
    # to combine them properly and still get the header correct. Levi mentioned having more
    # than one day listing per page, so they flow into one another, if that is the case then
    # there will have to be a number of different queries.
    # its possible I could try implementing this using loops, but I am afraid of what kind
    # of bugs might crop up if I had a database query in a loop - so i'm not going there.
    # IF django is lazy about the queries, then I'm totally saved here. And I think it is lazy.
    today = datetime.now()
    event_sets = []

    # error checking for num argument
    if int(num) < 0:
        num = 0

    # I should really combine this all into a function... there's a lot of shared code here
    if date == u'today':
        todays_events = upcoming_events.filter(
            start_time__year=today.year, 
            start_time__month=today.month,
            start_time__day=today.day)   
        pages = todays_events.count() > settings.EVENTS_PER_PAGE
        todays_events = todays_events.order_by('start_time')[int(num)*settings.EVENTS_PER_PAGE:settings.EVENTS_PER_PAGE]
        event_sets.append( EventSet(u"Today's Events", todays_events ) )
    elif date == u'tomorrow':
        tomorrow = today + timedelta(days=1)
        tomorrows_events = upcoming_events.filter(start_time__year=tomorrow.year, 
                                                 start_time__month=tomorrow.month,
                                                 start_time__day=tomorrow.day)
        pages = tomorrows_events.count() > settings.EVENTS_PER_PAGE
        tomorrows_events = tomorrows_events.order_by('start_time')[int(num)*settings.EVENTS_PER_PAGE:int(num)*settings.EVENTS_PER_PAGE + settings.EVENTS_PER_PAGE]
        event_sets.append( EventSet(u"Tomorrow's Events", tomorrows_events ) )
    elif date == u'this-weekend':
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
        pages = this_weekends_events.count() > settings.EVENTS_PER_PAGE
        this_weekends_events = this_weekends_events.order_by('start_time')[int(num)*settings.EVENTS_PER_PAGE:int(num)*settings.EVENTS_PER_PAGE + settings.EVENTS_PER_PAGE]
        event_sets.append( EventSet(u"Events This Weekend", this_weekends_events) )
    elif date == u'next-weekend':
        next_monday = today + timedelta(days=7-today.weekday())
        end = next_monday + timedelta(days=6-next_monday.weekday())
        start = next_monday + timedelta(days=4-next_monday.weekday())
        next_weekends_events = upcoming_events.filter(start_time__range=(start,end))
        pages = next_weekends_events.count() > settings.EVENTS_PER_PAGE
        next_weekends_events = next_weekends_events.order_by('start_time')[int(num)*settings.EVENTS_PER_PAGE:int(num)*settings.EVENTS_PER_PAGE + settings.EVENTS_PER_PAGE]
        event_sets.append( EventSet(u"Events Next Weekend", next_weekends_events) )
    elif date == u'this-week':
        end = today + timedelta(days=6-today.weekday())
        start = today
        this_weeks_events = upcoming_events.filter(start_time__range=(start,end))
        pages = this_weeks_events.count() > settings.EVENTS_PER_PAGE
        this_weeks_events = this_weeks_events.order_by('start_time')[int(num)*settings.EVENTS_PER_PAGE:int(num)*settings.EVENTS_PER_PAGE + settings.EVENTS_PER_PAGE]
        event_sets.append( EventSet(u"Events This Week", this_weeks_events ) )
    elif date == u'next-week':
        end = today + timedelta(days=13-today.weekday())
        start = today + timedelta(days=7-today.weekday())
        next_weeks_events = upcoming_events.filter(start_time__range=(start,end))
        pages = next_weeks_events.count() > settings.EVENTS_PER_PAGE
        next_weeks_events = next_weeks_events.order_by('start_time')[int(num)*settings.EVENTS_PER_PAGE:int(num)*settings.EVENTS_PER_PAGE + settings.EVENTS_PER_PAGE]
        event_sets.append( EventSet(u"Events Next Week", next_weeks_events) )    
    else:
        ISO8601_REGEX = re.compile(r'(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})')
        exact_date = ISO8601_REGEX.match(date)
        if exact_date:
            group = exact_date.groupdict()
            start = datetime(year=int(group["year"]), 
                             month=int(group["month"]), 
                             day=int(group["day"]) )
            end = start + timedelta(days=1)
            exact_day_events = upcoming_events.filter(start_time__range=(start,end))
            pages = exact_day_events.count() > settings.EVENTS_PER_PAGE
            exact_day_events = exact_day_events.order_by('start_time')[int(num)*settings.EVENTS_PER_PAGE:int(num)*settings.EVENTS_PER_PAGE + settings.EVENTS_PER_PAGE]
            event_sets.append( EventSet( u'Events for ' + start.date().isoformat() , exact_day_events))
            

    # NUMCODE: This code is here because the page numbers start at 1 (which is never displayed or linked to)
    # and according to the resident HCI guru, people like counting from 1
    # but I use it in the date filter code as a multiplier, which I want to start at 0
    num = num + 1
    page_less = num - 1
    if num < 2:
        page_more = 2
    else:
        page_more = num +1

    return render_to_response('events/browse_events.html',
                              { 'upcoming_events':upcoming_events,
                                'all_tags':all_tags,
                                'current_tags':old_tags,
                                'page_date':date,
                                'page_num':int(num),
                                'event_sets':event_sets,
                                'pages':pages,
                                'page_less':page_less,
                                'page_more':page_more},
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
