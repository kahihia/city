import datetime
import time
import json
import utils

from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage
from django.utils.safestring import mark_safe

from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib import messages

from django.middleware.csrf import get_token

from django.contrib.gis.geos import Point
from cities.models import City, Country, Region
from django.db.models import Q, Count
from event.filters import EventFilter

from event import DEFAULT_FROM_EMAIL

from event.models import Event, Venue, SingleEvent, Reminder, AuditEvent, FakeAuditEvent, FeaturedEvent
from accounts.models import VenueAccount
from event.utils import find_nearest_city

from event.forms import generate_form, SetupFeaturedForm

from taggit.models import Tag, TaggedItem

from ajaxuploader.views import AjaxFileUploader


def start(request):
    csrf_token = get_token(request)
    return render_to_response('import.html',
        {'csrf_token': csrf_token}, context_instance=RequestContext(request))


import_uploader = AjaxFileUploader()


def redirect(request):
    return HttpResponseRedirect(reverse('search_pad'))


def search_pad(request):
    start_date, end_date = utils.get_dates_from_request(request)
    start_time, end_time = utils.get_times_from_request(request)

    featured_events = Event.featured_events.all()

    featuredEventsFilter = EventFilter({}, queryset=featured_events)

    events = Event.future_events.all()

    events_all_count = events.count()

    params = request.GET.copy()

    if not "location" in params:
        params["location"] = "%s|%s" % (
            request.user_location_type,
            request.user_location_id
        )

    eventsFilter = EventFilter(params, queryset=events)

    top5_tags = TaggedItem.objects.filter(object_id__in=map(lambda event: event.id, events)) \
        .values('tag', 'tag__name') \
        .annotate(count=Count('id')) \
        .order_by('-count')[0:5]

    return render_to_response('events/search_pad.html', {
                                'featured_events': featured_events,
                                'featuredEventsFilter': featuredEventsFilter,
                                'events': events,
                                'eventsFilter': eventsFilter,
                                'top5_tags': top5_tags,
                                'events_all_count': events_all_count,
                                'start_date': start_date,
                                'end_date': end_date,
                                'start_time': start_time,
                                'end_time': end_time
                            }, context_instance=RequestContext(request))


def browse(request):
    start_date, end_date = utils.get_dates_from_request(request)
    start_time, end_time = utils.get_times_from_request(request)

    featured_events = Event.featured_events.all()

    featuredEventsFilter = EventFilter({}, queryset=featured_events)

    events = Event.future_events.all()

    params = request.GET.copy()

    if not "location" in params:
        params["location"] = "%s|%s" % (
            request.user_location_type,
            request.user_location_id
        )

    eventsFilter = EventFilter(params, queryset=events)

    tags = TaggedItem.objects.filter(object_id__in=map(lambda event: event.id, events)) \
        .values('tag', 'tag__name') \
        .annotate(count=Count('id')) \
        .order_by('-count')

    return render_to_response('events/browse_events.html', {
                                'featured_events': featured_events,
                                'featuredEventsFilter': featuredEventsFilter,
                                'events': events,
                                'eventsFilter': eventsFilter,
                                'tags': tags,
                                'start_date': start_date,
                                'end_date': end_date,
                                'start_time': start_time,
                                'end_time': end_time
                            }, context_instance=RequestContext(request))


def view_featured(request, slug=None):
    try:
        event = Event.future_events.get(slug=slug)
        # TODO: add filter by IP
        # event.viewed_times = event.viewed_times + 1
        # event.save()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_browse'))   
        
    event.featuredevent_set.all()[0].click() 

    return HttpResponseRedirect(reverse('event_view', args=(slug, ))) 


def view(request, slug=None):
    try:
        event = Event.future_events.get(slug=slug)
        # TODO: add filter by IP
        # event.viewed_times = event.viewed_times + 1
        # event.save()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_browse'))    

    opengraph = {'og:title': event.name,
                  'og:type': 'event',
                  'og:locale': 'en_US',
                  # 'og:image': 'http://' + settings.EVENT_EMAIL_SITE + event_picture_url(event, size=200),
                  'og:url': 'http://' + settings.EVENT_EMAIL_SITE + reverse('event_view', args=(event.slug,)),
                  'og:site_name': 'Cityfusion',
                  'fb:app_id': '330171680330072',
                  #'og:description' : '%s, %s' % (
                  #    event.start_time.strftime("%B %-1d"),
                  #    event.start_time.strftime('%-1I:%M %p'))
                  }

    return render_to_response('events/event_description.html', {
                                'event': event,
                                'browsing': True,
                                'opengraph': opengraph
                                },
                              context_instance=RequestContext(request))


def view_event_day(request, id):
    event_day = SingleEvent.objects.get(id=id)

    return render_to_response('events/event_day_description.html', {
                                'event_day': event_day
                            },
                            context_instance=RequestContext(request))


def save_venue(request):
    if request.POST["venue_name"]:
        name = request.POST["venue_name"]
        street = request.POST["street"]
        city = City.objects.get(id=int(request.POST["city_identifier"]))
        country = Country.objects.get(name='Canada')
        location = Point((
            float(request.POST["location_lng"]),
            float(request.POST["location_lat"])
        ))
        venue = Venue(name=name, street=street, city=city, country=country, location=location)
        venue.save()
    elif request.POST["place"]:
        name = request.POST["geo_venue"]
        street = request.POST["geo_street"]
        city = City.objects.filter(
            Q(name_std=request.POST["geo_city"].encode('utf8')) |
            Q(name=request.POST["geo_city"])
        )
        country = Country.objects.get(name='Canada')
        location = Point((
            float(request.POST["geo_longtitude"]),
            float(request.POST["geo_latitude"])
        ))

        if city.count() > 1:
            city = find_nearest_city(city, location)
        elif not city.count():
            city = City.objects.distance(location).order_by('distance')[0]
        else:
            city = city[0]
        venue, created = Venue.objects.get_or_create(name=name, street=street, city=city, country=country, location=location)
    return venue


def save_when_and_description(request, event_obj):
    when_json = json.loads(request.POST["when_json"])
    description_json = json.loads(request.POST["description_json"])

    event_obj.description = description_json['default']

    for year, months in when_json.iteritems():
        for month, days in months.iteritems():
            for day, times in days.iteritems():
                date = datetime.datetime(int(year), int(month), int(day), 0, 0)
                if date.strftime("%m/%d/%Y") in description_json['days']:
                    description = description_json['days'][date.strftime("%m/%d/%Y")]
                else:
                    description = ""
                start_time = time.strptime(times["start"], '%I:%M %p')
                start = datetime.datetime(int(year), int(month), int(day), start_time[3], start_time[4])

                end_time = time.strptime(times["end"], '%I:%M %p')
                end = datetime.datetime(int(year), int(month), int(day), end_time[3], end_time[4])

                single_event = SingleEvent(
                    event=event_obj,
                    start_time=start.strftime('%Y-%m-%d %H:%M'),
                    end_time=end.strftime('%Y-%m-%d %H:%M'),
                    description=description
                )
                single_event.save()


def send_event_details_email(event_obj):
    #email the user
    current_site = settings.EVENT_EMAIL_SITE
    subject = render_to_string('events/creation_email_subject.txt', {
            'site': current_site,
            'title': mark_safe(event_obj.name)
        })

    subject = ''.join(subject.splitlines())  # Email subjects are all on one line

    message = render_to_string('events/creation_email.txt', {
            'authentication_key': event_obj.authentication_key,
            'slug': event_obj.slug,
            'site': current_site
        })

    msg = EmailMessage(subject,
               message,
               DEFAULT_FROM_EMAIL,
               [event_obj.email])
    msg.content_subtype = 'html'
    msg.send()


def link_venue_with_account(venue, account):
    venue_account, created = VenueAccount.objects.get_or_create(venue=venue)
    venue_account.accounts.add(account)


def save_event(request, form):

    venue = save_venue(request)

    event_obj = form.save()
    event_obj.venue = venue

    save_when_and_description(request, event_obj)

    if request.user.is_authenticated():
        #if logged in, use the users info to complete form
        event_obj.owner = request.user
        event_obj.email = request.user.email  # don't really need this line

    if request.POST["picture_src"]:
        event_obj.picture.name = request.POST["picture_src"].replace(settings.MEDIA_URL, "")

    event_obj = event_obj.save()  # save to the database
    # form.save_m2m()  # needed for many-to-many fields (i.e. the event tags)
    return event_obj


def create(request, form_class=None, success_url=None, template_name='events/create_event.html'):
    if form_class == None:
        exclude = ['owner', 'authentication_key', 'slug']
        if request.user.is_authenticated():
            exclude.append('email')
        else:
            return HttpResponseRedirect('/accounts/login/')
        form_class = generate_form(*exclude)

    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            event_obj = save_event(request, form)
            send_event_details_email(event_obj)

            # on success, redirect to the home page by default
            # if the user is authenticated, take them to their event page
            if success_url is None:
                success_url = reverse('event_created', kwargs={'slug': event_obj.slug})
            #send user off into the abyss...
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()

    #Send out the form
    context = RequestContext(request)
    return render_to_response(template_name, {
            'form': form,
            'posting': True,
            'location': request.location,
        }, context_instance=context)


def created(request, slug=None):
    if slug is None:
        raise Http404

    return render_to_response('events/creation_complete.html', {
            'slug': slug,
            'posting': True,
        }, context_instance=RequestContext(request))


def initial_for_event_form(event_obj):
    venue = event_obj.venue

    full_parts = [x for x in [venue.name, venue.street, venue.city.name, venue.country.name] if x]
    place = {
        "full": ", ".join(full_parts),
        "venue": venue.name,
        "street": venue.street,
        "city": venue.city.name,
        "country": venue.country.name,
        "longtitude": venue.location.y,
        "latitude": venue.location.x
    }

    location = (venue.location.y, venue.location.x)

    when_json = {}
    description_json = {
        "default": event_obj.description,
        "days": {}
    }

    single_events = SingleEvent.objects.filter(event=event_obj)

    for se in single_events:
        start_time = se.start_time
        year = start_time.year
        month = start_time.month
        day = start_time.day

        if not year in when_json:
            when_json[year] = {}

        if not month in when_json[year]:
            when_json[year][month] = {}

        when_json[year][month][day] = {
            "start": start_time.strftime('%I:%M %p'),
            "end": se.end_time.strftime('%I:%M %p')
        }

        description_json["days"][start_time.strftime("%m/%d/%Y")] = se.description

    return {
            "place": place,
            "location": location,
            "picture_src": "/media/%s" % event_obj.picture,
            "when_json": json.dumps(when_json),
            "description_json": json.dumps(description_json)
        }


def edit(request,
         form_class=None, success_url=None, authentication_key=None,
         template_name='events/edit_event.html'):

    # Define the form to be used. This allows for anonymous creation of events.
    if form_class == None:
        form_class = generate_form('owner', 'authentication_key', 'slug', 'email')

    # Event object is retrieved based on incoming path hash
    # If the hash does not match an existing event, the user
    # is redirected to the event creation page.
    try:
        event_obj = Event.events.get(authentication_key__exact=authentication_key)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_create'))

    # Set the return address
    if success_url is None:
        success_url = reverse('event_view', kwargs={'slug': event_obj.slug})

    # Verify and save the form to model
    if request.method == 'POST':
        form = form_class(instance=event_obj, data=request.POST)
        if form.is_valid():
            # Remove existing single events
            SingleEvent.objects.filter(event=event_obj).delete()

            event_obj = save_event(request, form)
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(
            instance=event_obj,
            initial=initial_for_event_form(event_obj)
        )

    # Edit the event
    context = RequestContext(request)
    return render_to_response(template_name, {
                                'form': form,
                                'event': event_obj,
                                'location': request.location,
                            },
                            context_instance=context)


def remove(request, authentication_key):
    event_obj = Event.events.get(authentication_key__exact=authentication_key)
    event_obj.delete()

    return HttpResponseRedirect(reverse('private_venue_account', args=(request.current_venue_account.slug, )))


def setup_featured(request, authentication_key):
    account = Account.objects.get(user_id=request.user.id)
    event_obj = Event.events.get(authentication_key__exact=authentication_key)
    venue_account = account.venueaccount_set.get(venue=event_obj.venue)
    featured_event = FeaturedEvent(
        event=event_obj,
        venue_account=venue_account,
        start_time=datetime.date.today(),
        end_time=datetime.date.today() + datetime.timedelta(days=15)
    )

    venue_account_featured_stats = FeaturedEvent.objects.filter(venue_account=venue_account)

    form = SetupFeaturedForm(
        instance=featured_event
    )

    if request.method == 'POST':
        form = SetupFeaturedForm(instance=featured_event, data=request.POST)

        if form.is_valid():
            form.save()
            # TODO: here will be redirect to payments
            return HttpResponseRedirect(reverse('private_venue_account', args=(request.current_venue_account.slug, )))

    return render_to_response('events/setup_featured_event.html', {
            'form': form,
            'featured_events_stats': venue_account_featured_stats
        }, context_instance=RequestContext(request))


def make_featured(request, authentication_key):
    event_obj = Event.events.get(authentication_key__exact=authentication_key)
    event_obj.featured = True
    event_obj.save()

    return HttpResponseRedirect(reverse('private_venue_account', args=(request.current_venue_account.slug, )))


def daily(start, end, weekday=False, day_delta=1):
    """
    Pre: start is a date
         end is a date
         weekday is a boolean, to pick if we are skipping saturdays and sundays
         day_delta is an integer, to pick how many days to skip between events.
    Returns: a list of days specified by the inputs
    """
    date_list = []
    if weekday:
        #TODO: implement week day recurrance
        pass
    else:
        delta = datetime.timedelta(days=day_delta)
        current = start + delta
        while current <= end:
            date_list.append(current)
            current += delta
    return date_list


def ason(request):
    tag_list = []
    all_events = Event.events.all()
    for j in all_events:
        for u in j.tags.all():
            tag_list.append(u.name)

    return HttpResponse(json.dumps(tag_list), mimetype="application/json")


def reminder(request, event_id):
    if request.user.is_authenticated():
        mail = request.user.email
        search = Event.events.get(id=event_id)
        saves = Reminder(event=search.name, email=mail, date=search.start_time)
        saves.save()
        messages.add_message(request, messages.SUCCESS, 'Event reminder will be sent')
    else:
        return HttpResponseRedirect('/accounts/register/')
    return HttpResponseRedirect(request.GET['next'])


def city_tags(request):
    city = None
    if request.method == 'POST':
        if "city_identifier" in request.POST:
            city = City.objects.get(id=int(request.POST["city_identifier"]))

        elif "geo_city" in request.POST:
            cities = City.objects.filter(
                Q(name_std=request.POST["geo_city"].encode('utf8')) |
                Q(name=request.POST["geo_city"])
            )
            if cities.count():
                city = cities[0]

        if city:
            tags = Event.events.filter(venue__city=city).select_related('tags').values('tags')
            tags = set([tag['tags'] for tag in tags if tag['tags']])
        else:
            tags = []

        tags = Tag.objects.filter(Q(id__in=tags) |
            Q(name__in=["Free", "Wheelchair"])
        ).values()
        return HttpResponse(json.dumps({"tags": list(tags)}), mimetype="application/json")


def audit_event_list(request):
    audit_events = AuditEvent.objects.all()
    return render_to_response("audit/event_list.html", {'audit_events': audit_events}, context_instance=RequestContext(request))


def audit_event_remove(request, id):
    audit_event = AuditEvent.objects.get(pk=id)
    audit_event.delete()
    return audit_event_list(request)


def audit_event_edit(request, id):
    audit_event = AuditEvent.objects.get(pk=id)
    return render_to_response("audit/event_edit.html", {'audit_event': audit_event}, context_instance=RequestContext(request))


def audit_event_update(request, id):
    audit_event = AuditEvent.objects.get(pk=id)
    audit_event_fake = FakeAuditEvent.objects.get(pk=id)
    event_obj = Event.events.get(pk=id)
    audit_event.phrases.clear()
    audit_event_fake.delete()

    event_obj.audited = True
    event_obj.name = request.POST["name"]
    event_obj.description = request.POST["description"]
    event_obj.save()
    return audit_event_list(request)


def audit_event_admin_update(request, id):
    audit_event = AuditEvent.objects.get(pk=id)
    audit_event_fake = FakeAuditEvent.objects.get(pk=id)
    event_obj = Event.events.get(pk=id)
    audit_event.phrases.clear()
    audit_event_fake.delete()

    event_obj.audited = True
    event_obj.name = request.POST["name"]
    event_obj.description = request.POST["description"]
    event_obj.save()
    return HttpResponseRedirect('/admin/event/auditevent')


def audit_event_approve(request, id):
    audit_event = AuditEvent.objects.get(pk=id)
    audit_event_fake = FakeAuditEvent.objects.get(pk=id)
    event_obj = Event.events.get(pk=id)
    audit_event.phrases.clear()
    audit_event_fake.delete()

    event_obj.audited = True
    event_obj.save()
    return audit_event_list(request)


def nearest_venues(request):
    if request.method == 'GET':
        search = request.GET.get("search", "")

        venues = Venue.with_active_events()
        if search:
            venues = venues.filter(Q(name__icontains=search) | Q(city__name__icontains=search))
        if request.location:
            venues = venues.distance(Point(request.location)).order_by('-distance')[:10]

        return HttpResponse(json.dumps({
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "city": venue.city.name_std
            } for venue in venues.select_related("city")]
        }), mimetype="application/json")


def save_active_tab(request, page, tab):
    request.session[page] = tab
    return HttpResponse("OK")


def location_autocomplete(request):
    """
        I should give user opportunity to choose region where from events is interesting for him. It can be whole Canada, regions or city
    """

    if request.method == 'GET':
        canada = Country.objects.get(name="Canada")

        locations = []

        kwargs = {
            "country": canada
        }

        search = request.GET.get("search", "")

        if search:
            kwargs["name__icontains"] = search

        cities = City.objects.filter(**kwargs)

        if request.location:
            cities = cities.distance(Point(request.location)).order_by('-distance')

        cities = cities[0:5]

        for city in cities:
            if city.region:
                name = "%s, %s, %s" % (city.name, city.region.name, city.country.name)
            else:
                name = "%s, %s" % (city.name, city.country.name)
            locations.append({
                "id": city.id,
                "type": "city",
                "name": name
            })

        regions = Region.objects.filter(**kwargs)[:5]

        for region in regions:
            locations.append({
                "id": region.id,
                "type": "region",
                "name": "%s, %s" % (region.name, region.country.name)
            })

        if not search or search.lower() in "canada":
            locations.append({
                "id": canada.id,
                "type": "country",
                "name": "Canada"
            })

        return HttpResponse(json.dumps({
            "locations": locations
        }), mimetype="application/json")
