import datetime
import json
import utils

from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.middleware.csrf import get_token
from django.contrib.gis.geos import Point
from django.db.models import Q, Count, F
from django.forms.util import ErrorList
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.contrib import messages

from taggit.models import Tag, TaggedItem
from moneyed import Money, CAD
from django_facebook.decorators import facebook_required

from cities.models import City, Country, Region
from event.filters import EventFilter
from event.models import Event, Venue, SingleEvent, AuditEvent, FakeAuditEvent, FeaturedEvent, FeaturedEventOrder
from event.services import facebook_services, location_service, event_service
from event.forms import SetupFeaturedForm, CreateEventForm, EditEventForm
from ajaxuploader.views import AjaxFileUploader
from accounts.decorators import native_region_required
from accounts.models import VenueAccount, AccountTaxCost
from decimal import Decimal
from accounts.models import Account


def start(request):
    csrf_token = get_token(request)
    return render_to_response('import.html',
        {'csrf_token': csrf_token}, context_instance=RequestContext(request))


import_uploader = AjaxFileUploader()


def redirect(request):
    return HttpResponseRedirect(reverse('event_browse'))


def search_pad(request):
    start_date, end_date = utils.get_dates_from_request(request)
    start_time, end_time = utils.get_times_from_request(request)

    events = SingleEvent.future_events.all()

    events_all_count = events.count()

    params = request.GET.copy()
    location_from_user_choice = location_service.LocationFromUserChoice(request)
    if not "location" in params:
        params["location"] = "%s|%s" % (
            location_from_user_choice.location_type,
            location_from_user_choice.location_id,
        )

    eventsFilter = EventFilter(params, queryset=events, account=request.account)

    if "search" in params:
        top10_tags = TaggedItem.objects.filter(object_id__in=map(lambda event: event.event.id, eventsFilter.qs())) \
            .values('tag_id', 'tag__name') \
            .annotate(count=Count('id')) \
            .order_by('-count')[:10]
    else:
        top10_tags = TaggedItem.objects.filter(object_id__in=eventsFilter.qs().values_list("event_id", flat=True)) \
            .values('tag_id', 'tag__name') \
            .annotate(count=Count('id')) \
            .order_by('-count')[:10]


    return render_to_response('events/search_pad.html', {
                                'events': events,
                                'eventsFilter': eventsFilter,
                                'top10_tags': top10_tags,
                                'events_all_count': events_all_count,
                                'start_date': start_date,
                                'end_date': end_date,
                                'start_time': start_time,
                                'end_time': end_time
                            }, context_instance=RequestContext(request))


def browse(request):
    start_date, end_date = utils.get_dates_from_request(request)
    start_time, end_time = utils.get_times_from_request(request)

    region = location_service.LocationForFeaturedEvent(request).canadian_region
    featured_event_query = Q(featuredevent__all_of_canada=True)
    if region:
        featured_event_query = featured_event_query | Q(featuredevent__regions__id=region.id)

    featured_events = Event.featured_events\
        .filter(featured_event_query)\
        .order_by('?')\
        .annotate(Count("id"))

    events = SingleEvent.future_events.all()

    params = request.GET.copy()
    location_from_user_choice = location_service.LocationFromUserChoice(request)
    if not "location" in params:
        params["location"] = "%s|%s" % (
            location_from_user_choice.location_type,
            location_from_user_choice.location_id,
        )

    eventsFilter = EventFilter(params, queryset=events)

    if "search" in params:
        tags = TaggedItem.objects.filter(object_id__in=map(lambda event: event.event.id, eventsFilter.qs())) \
            .values('tag_id', 'tag__name') \
            .annotate(count=Count('id')) \
            .order_by('-count')
    else:
        tags = TaggedItem.objects.filter(object_id__in=eventsFilter.qs().values_list("event_id", flat=True)) \
            .values('tag_id', 'tag__name') \
            .annotate(count=Count('id')) \
            .order_by('-count')


    return render_to_response('events/browse_events.html', {
                                'featured_events': featured_events,
                                'events': events,
                                'eventsFilter': eventsFilter,
                                'tags': tags,
                                'start_date': start_date,
                                'end_date': end_date,
                                'start_time': start_time,
                                'end_time': end_time
                            }, context_instance=RequestContext(request))


def view_featured(request, slug, date):
    try:
        event = Event.future_events.get(slug=slug, start_time__startswith=date)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_browse'))   
        
    event.featuredevent_set.all()[0].click() 

    return HttpResponseRedirect(reverse('event_view', args=(slug, date))) 


def view(request, slug, date=None):
    try:
        if date:
            event = SingleEvent.future_events.filter(event__slug=slug, start_time__startswith=date)[0]
        else:
            event = Event.future_events.get(slug=slug).next_day()

        if not event:
            raise ObjectDoesNotExist

    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_browse'))


    if not event.viewed_times:
        Event.events.filter(id=event.event_identifier).update(viewed_times=1)
    else:
        Event.events.filter(id=event.event_identifier).update(viewed_times=F('viewed_times')+1)

    venue = event.venue

    events_from_venue = SingleEvent.future_events.filter(event__venue_id=venue.id).select_related("event__venue", "event__venue__city")
    if date:
        events_from_venue = events_from_venue.exclude(id=event.id)

    return render_to_response('events/event_detail_page.html', {
            'event': event,
            'events_from_venue': events_from_venue,
            'now': datetime.datetime.now()
        }, context_instance=RequestContext(request))


@login_required
def create(request, success_url=None, template_name='events/create/create_event.html'):
    if request.method == 'POST':
        form = CreateEventForm(account=request.account, data=request.POST)
        if form.is_valid():
            try:
                event = event_service.save_event(request.user, request.POST, form)

                event_service.send_event_details_email(event)

                if success_url is None:
                    success_url = reverse('event_created', kwargs={ 'slug': event.slug })

                return HttpResponseRedirect(success_url)

            except:
                form._errors['__all__'] = ErrorList(["Unhandled exception. Please inform administrator."])

    else:
        form = CreateEventForm(account=request.account, initial={
            "venue_account_owner": request.current_venue_account
        })


    context = RequestContext(request)
    return render_to_response(template_name, {
            'form': form,
            'posting': True,
            'location': request.user_location["user_location_lat_lon"],
        }, context_instance=context)


@login_required
def create_from_facebook(request):
    if request.method == 'POST':
        success = False
        form = CreateEventForm(account=request.account, data=request.POST)
        if form.is_valid():
            try:
                facebook_event_id = request.POST['facebook_event_id']
                event = event_service.save_event(request.user, request.POST, form)
                facebook_services.attach_facebook_event(int(facebook_event_id), event)
                success = True
            except Exception:
                form._errors['__all__'] = ErrorList(["Unhandled exception. Please inform administrator."])
            info = ''
        else:
            info = form.errors

        return HttpResponse(
            json.dumps({'success': success, 'info': info}),
            mimetype='application/json')
    else:
        event_data = facebook_services.get_prepared_event_data(request, request.GET)
        form = CreateEventForm(account=request.account, data=event_data)
        return render_to_response('events/create/create_event_popup.html', {'form': form},
                                  context_instance=RequestContext(request))


@login_required
@facebook_required
def post_to_facebook(request, id):
    event = Event.events.get(pk=id)
    if request.user.id == event.owner.id:
        if not event.facebook_event:
            try:
                facebook_event_id = facebook_services.create_facebook_event(event, request)
                facebook_services.attach_facebook_event(int(facebook_event_id), event)
                messages.success(request, 'Event was successfully posted to FB.')
            except Exception as e:
                messages.error(request, e.message)
        else:
            messages.error(request, 'Event has already been posted to FB.')
    else:
        messages.error(request, 'You do not have permission to publish this event.')

    return HttpResponseRedirect(reverse('event_view', kwargs={'slug': event.slug}))


def created(request, slug=None):
    if slug is None:
        raise Http404

    return render_to_response('events/create/creation_complete.html', {
            'slug': slug,
            'posting': True,
        }, context_instance=RequestContext(request))


@login_required
def edit(request, success_url=None, authentication_key=None, template_name='events/edit/edit_event.html'):
    try:
        event = Event.events.get(authentication_key__exact=authentication_key)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_create'))

    if request.method == 'POST':
        form = EditEventForm(account=request.account, instance=event, data=request.POST)
        if form.is_valid():
            # try:
            event_service.save_event(request.user, request.POST, form)
            return HttpResponseRedirect(
                reverse('event_view', kwargs={'slug': event.slug})
            )

            # except:
            #     form._errors['__all__'] = ErrorList(["Unhandled exception. Please inform administrator."])
    else:
        form = EditEventForm(
            account=request.account,
            instance=event,
            initial=event_service.prepare_initial_event_data_for_edit(event)
        )

    return render_to_response(template_name, {
                                'form': form,
                                'event': event                            
                            },
                            context_instance=RequestContext(request))


@login_required
def copy(request, authentication_key, template_name='events/create/copy_event.html'):
    if request.method == 'POST':
        form = CreateEventForm(account=request.account, data=request.POST)
        if form.is_valid():
            event_obj = event_service.save_event(request.user, request.POST, form)
            event_service.send_event_details_email(event_obj)

            success_url = reverse('event_created', kwargs={ 'slug': event_obj.slug })

            return HttpResponseRedirect(success_url)
    else:
        basic_event = Event.events.get(authentication_key__exact=authentication_key)   

        event = Event(
            name=basic_event.name, 
            description=basic_event.description,
            price=basic_event.price,
            website=basic_event.website,
            tickets=basic_event.tickets,
            owner=basic_event.owner,
            venue_account_owner=basic_event.venue_account_owner,
            picture=basic_event.picture,
            cropping=basic_event.cropping,
        )

        form = CreateEventForm(
            account=request.account, 
            instance=event, 
            initial=event_service.prepare_initial_event_data_for_copy(basic_event)
        )

    return render_to_response(template_name, {
            'form': form,
            'posting': True
        }, context_instance=RequestContext(request))    


@login_required
def remove(request, authentication_key):
    event = Event.events.get(authentication_key__exact=authentication_key)
    event.delete()

    url = request.META.get('HTTP_REFERER', reverse('event_browse'))

    return HttpResponseRedirect(url)


@login_required
@native_region_required(why_message="native_region_required")
def setup_featured(request, authentication_key):
    account = request.account
    event = Event.events.get(authentication_key__exact=authentication_key)    

    featured_event = FeaturedEvent(
        event=event,
        owner=account,
        start_time=datetime.date.today(),
        end_time=datetime.date.today() + datetime.timedelta(days=15)
    )

    venue_account_featured_stats = FeaturedEvent.objects.filter(event__venue_id=event.venue.id)

    form = SetupFeaturedForm(
        account=account,
        instance=featured_event
    )

    if request.method == 'POST':
        form = SetupFeaturedForm(account=account, instance=featured_event, data=request.POST)

        if form.is_valid():
            featured_event = form.save()

            budget_type = request.POST["budget_type"]

            if budget_type == "BONUS":
                featured_event.active = True
                featured_event.save()
                budget = Decimal(request.POST["bonus_budget"])
                Account.objects.filter(user_id=request.user.id).update(bonus_budget=F("bonus_budget")-budget)

                return HttpResponseRedirect('/accounts/%s/' % request.user.username)

            if budget_type == "REAL":
                cost = (featured_event.end_time - featured_event.start_time).days * Money(2, CAD)
                total_price = cost

                for tax in account.taxes():
                    total_price = total_price + (cost * tax.tax)

                order = FeaturedEventOrder(
                    cost=cost,
                    total_price=total_price,
                    featured_event=featured_event,
                    account=account
                )

                order.save()

                for tax in account.taxes():
                    account_tax_cost = AccountTaxCost(account_tax=tax, cost=cost*tax.tax, tax_name=tax.name)
                    account_tax_cost.save()
                    order.taxes.add(account_tax_cost)
                

                return HttpResponseRedirect(reverse('setup_featured_payment', args=(str(order.id),)))

    return render_to_response('events/setup_featured_event.html', {
            'form': form,
            'featured_events_stats': venue_account_featured_stats,
            'account': account
        }, context_instance=RequestContext(request))


def payment(request, order_id):
    order = get_object_or_404(FeaturedEventOrder, pk=order_id)

    # form = PaypalConfirmationForm()

    return render_to_response('featured/payment.html', {
        "order": order
    }, context_instance=RequestContext(request))


def featured_event_order(request, order_id):
    order = get_object_or_404(FeaturedEventOrder, pk=order_id)
    payment = order.featuredeventpayment_set.all()[0]
    return render_to_response('featured/order.html', {
        "order": order,
        "payment": payment
    }, context_instance=RequestContext(request))


def ason(request):
    tag_list = []
    all_events = Event.events.all()
    for j in all_events:
        for u in j.tags.all():
            tag_list.append(u.name)

    return HttpResponse(json.dumps(tag_list), mimetype="application/json")


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

        elif "venue_id" in request.POST:
            city = Venue.objects.get(id=int(request.POST['venue_id'])).city

        elif "venue_account_id" in request.POST:
            city = VenueAccount.objects.get(id=int(request.POST['venue_account_id'])).venue.city

        if city:
            tags = Event.events.filter(venue__city=city).select_related('tags').values('tags')
            tags = set([tag['tags'] for tag in tags if tag['tags']])
        else:
            tags = []

        tags = Tag.objects.filter(
            Q(id__in=tags) | Q(name__in=["Free", "Wheelchair"])
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
            venues = venues.distance(Point(request.location)).order_by('distance')[:10]

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


@require_GET
def location_autocomplete(request):
    """
        I should give user opportunity to choose region where from events is interesting for him. It can be whole Canada, regions or city
    """

    canada = Country.objects.get(name="Canada")

    locations = []

    kwargs = {
        "country": canada
    }

    search = request.GET.get("search", "")

    if search: 
        kwargs["name__icontains"] = search

    cities = City.objects.filter(**kwargs)

    if request.user_location and request.user_location["user_location_lat_lon"]:
        cities = cities.distance(Point(request.user_location["user_location_lat_lon"][::-1])).order_by('distance')

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

    regions = Region.objects.filter(**kwargs)[:3]

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


@require_GET
def suggest_cityfusion_venue(request):
    search = request.GET.get("search", "")

    if search:
        venues = Venue.objects.filter(suggested=True).filter(
            Q(name__icontains=search)|Q(street__icontains=search)|Q(city__name__icontains=search)
        )[:5]
    else:
        venues = Venue.objects.filter(suggested=True)[:5]

    return HttpResponse(json.dumps({
        "venues": map(lambda venue: { 
            "id": venue.id,
            "full_name": venue.__unicode__(),
            "name": venue.name,
            "street": venue.street,
            "city_name": venue.city.name,
            "city_id": venue.city.id,
            "lat": venue.location.y,
            "lng": venue.location.x,
        }, venues)
    }), mimetype="application/json")


@require_GET
def set_browser_location(request):
    lat_lon = (
        float(request.GET['latitude']),
        float(request.GET['longitude']),
    )

    from_browser = location_service.LocationFromBrowser(request)

    status = "SAME"

    if not from_browser.lat_lon:
        status = "REFRESH"

    from_browser.lat_lon = lat_lon    

    return HttpResponse(json.dumps({
        "status": status
    }), mimetype="application/json")    
