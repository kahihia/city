import datetime
import json
import utils
import mimetypes

from django.core.urlresolvers import reverse, resolve, Resolver404
from django.core.exceptions import ObjectDoesNotExist
from django.http import (Http404,
                         HttpResponseRedirect,
                         HttpResponse,
                         HttpResponseServerError,
                         HttpResponsePermanentRedirect)
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.middleware.csrf import get_token
from django.contrib.gis.geos import Point
from django.db.models import Q, Count, F
from django.db import transaction
from django.forms.util import ErrorList
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.conf import settings

from cities.models import City, Country, Region
from django_facebook.decorators import facebook_required
from taggit.models import Tag, TaggedItem
from moneyed import CAD

from accounts.decorators import native_region_required
from accounts.models import Account, VenueAccount
from ajaxuploader.views import AjaxFileUploader
from event.filters import EventFilter, FunctionFilter
from event.models import (Event, Venue, SingleEvent, AuditEvent, FakeAuditEvent,
                          FeaturedEvent, FeaturedEventOrder, EventSlug)
from event.model_decorators import EventModelDecorator
from event.services import facebook_services, location_service, event_service, featured_service
from event.forms import CreateEventForm, EditEventForm, SetupFeaturedForm
from event.payments.processors import process_setup_featured
from home.models import Page
from venues.services import venue_service


def start(request):
    csrf_token = get_token(request)
    return render_to_response('import.html',
        {'csrf_token': csrf_token}, context_instance=RequestContext(request))


import_uploader = AjaxFileUploader()


def redirect(request):
    return HttpResponseRedirect(reverse('event_browse'))


def search_pad(request):
    search_params = ["search", "tag", "period", "start_date", "end_date", "start_time", "end_time", "function"]
    start_date, end_date = utils.get_dates_from_request(request)
    start_time, end_time = utils.get_times_from_request(request)

    params = request.GET.copy()

    if set(search_params) & set(params.keys()):
        events = SingleEvent.future_events.all()
    else:
        events = SingleEvent.homepage_events.all()

    events_all_count = events.count()

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
                                'location_name': location_from_user_choice.location_name,
                                'eventsFilter': eventsFilter,
                                'top10_tags': top10_tags,
                                'events_all_count': events_all_count,
                                'start_date': start_date,
                                'end_date': end_date,
                                'start_time': start_time,
                                'end_time': end_time
                            }, context_instance=RequestContext(request))


def browse(request, *args, **kwargs):
    search_params = ["search", "tag", "period", "start_date", "end_date", "start_time", "end_time", "function"]
    start_date, end_date = utils.get_dates_from_request(request)
    start_time, end_time = utils.get_times_from_request(request)

    featured_events = featured_service.featured_events_for_region(request)

    params = request.GET.copy()
    if 'extra_params' in kwargs:
        params.update(kwargs['extra_params'])

    if 'function' in params and params['function'] in FunctionFilter.SPLIT_FUNCTIONS:
        events = SingleEvent.future_events.all()
    else:
        events = SingleEvent.homepage_events.all()

    
    location_from_user_choice = location_service.LocationFromUserChoice(request)
    if not "location" in params:
        params["location"] = "%s|%s" % (
            location_from_user_choice.location_type,
            location_from_user_choice.location_id,
        )

    tag_page = kwargs['extra_params']['tag'] if 'extra_params' in kwargs and 'tag' in kwargs['extra_params'] else ''
    eventsFilter = EventFilter(params, queryset=events, account=request.account, tag_page=tag_page)

    if 'search' in params:
        tags = TaggedItem.objects.filter(object_id__in=map(lambda event: event.event.id, eventsFilter.qs())) \
            .values('tag_id', 'tag__name') \
            .annotate(count=Count('id'))
    else:
        tags = TaggedItem.objects.filter(object_id__in=eventsFilter.qs().values_list("event_id", flat=True)) \
            .values('tag_id', 'tag__name') \
            .annotate(count=Count('id'))

    if 'sort' in params and params['sort'] == 'abc':
        tags = tags.order_by('tag__name')
    else:
        tags = tags.order_by('-count')

    try:
        page_info = Page.objects.get(alias='home')
    except Page.DoesNotExist:
        page_info = {}

    return render_to_response('events/browse_events.html', {
                                'page_type': 'index',
                                'location_name': location_from_user_choice.location_name,
                                'featured_events': featured_events,
                                'events': events,
                                'eventsFilter': eventsFilter,
                                'tags': tags,
                                'start_date': start_date,
                                'end_date': end_date,
                                'start_time': start_time,
                                'end_time': end_time,
                                'period': params.get('period', ''),
                                'tag_page': kwargs['extra_params']['tag'] if 'extra_params' in kwargs
                                and 'tag' in kwargs['extra_params'] else '',
                                'page_info': page_info
                            }, context_instance=RequestContext(request))


def view_featured(request, slug, date=None):
    try:
        event = Event.future_events.get(eventslug__slug=slug)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_browse'))

    FeaturedEvent.click_featured_events(event.featuredevent_set.all())

    if date:
        return HttpResponseRedirect(reverse('event_view', args=(slug, date)))
    else:
        return HttpResponseRedirect(reverse('event_view', args=(slug, )))


def view(request, slug, date=None):
    try:
        if date:
            try:
                event = SingleEvent.future_events.filter(
                    Q(event__eventslug__slug=slug) & (Q(start_time__startswith=date) | Q(event__event_type="MULTIDAY"))
                )[0]
            except:
                raise ObjectDoesNotExist
        else:
            try:
                event = SingleEvent.future_events.get(event__eventslug__slug=slug,
                                                      event__event_type="MULTIDAY",
                                                      is_occurrence=False)
            except:
                event = Event.future_events.get(eventslug__slug=slug).next_day()

        if not event:
            raise ObjectDoesNotExist

    except ObjectDoesNotExist:
        return HttpResponsePermanentRedirect(reverse('home'))

    SingleEvent.objects.filter(id=event.id).update(viewed=F("viewed")+1)
    return render_to_response('events/event_detail_page.html', {
            'event': event,
            'now': datetime.datetime.now()
        }, context_instance=RequestContext(request))


@login_required
@transaction.commit_manually
def create(request, success_url=None, template_name='events/create/create_event.html'):
    if request.method == 'POST':
        form = CreateEventForm(account=request.account, data=request.POST, by_admin=request.user.is_staff)
        if form.is_valid():
            try:
                event = event_service.save_event(request.user, request.POST, form)
                event_service.send_event_details_email(event)
            except Exception:
                response = HttpResponseServerError()
                transaction.rollback()
                return response
            else:
                if success_url is None:
                    success_url = reverse('event_created', kwargs={'slug': event.slug})

                response = HttpResponseRedirect(success_url)
                transaction.commit()
                return response

            # except:
            #     form._errors['__all__'] = ErrorList(["Unhandled exception. Please inform administrator."])

    else:
        form = CreateEventForm(account=request.account, initial={
            "venue_account_owner": request.current_venue_account
        }, by_admin=request.user.is_staff)

    context = RequestContext(request)
    response = render_to_response(template_name, {
        'form': form,
        'posting': True,
        'location': request.user_location["user_location_lat_lon"],
    }, context_instance=context)

    transaction.commit() # unavoidable action
    return response


@login_required
def create_from_facebook(request):
    if request.method == 'POST':
        success = False
        form = CreateEventForm(account=request.account, data=request.POST, by_admin=request.user.is_staff)
        if form.is_valid():
            try:
                facebook_event_id = request.POST['facebook_event_id']
                event_service.save_event(request.user, request.POST, form)
                facebook_services.save_facebook_event(facebook_event_id)
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
        form = CreateEventForm(account=request.account, data=event_data, by_admin=request.user.is_staff)
        return render_to_response('events/create/create_event_popup.html', {'form': form},
                                  context_instance=RequestContext(request))


@login_required
@facebook_required
def post_to_facebook_ajax(request):
    success, error, facebook_event_ids = False, '', {}

    event_id = request.POST.get('event_id')
    facebook_owner_type = request.POST.get('owner_type')
    try:
        event = Event.events.get(pk=event_id)
    except Event.DoesNotExist as e:
        event, error = None, e.message

    if event:
        try:
            if facebook_owner_type == 'user':
                facebook_owner_id = facebook_services.get_facebook_user_id(request)
            else:
                facebook_owner_id = request.POST.get('page_id')

            facebook_event_ids = facebook_services.create_facebook_event(event, request, facebook_owner_id, facebook_owner_type)
            success = True
        except Exception as e:
            error = e.message
    else:
        error = 'Event does not exists'

    params = {'success': success, 'error': error, 'facebook_event_ids': facebook_event_ids}

    if error and event:
        params['event_link'] = reverse('event_edit', kwargs={'authentication_key': event.authentication_key})

    return HttpResponse(json.dumps(params), mimetype='application/json')


@login_required
def bind_to_venue(request):
    success, error = False, ''
    event = load_model(Event, request.POST.get('event_id', 0), 'events')
    venue_account = load_model(VenueAccount, request.POST.get('venue_account_id', 0))

    if event and venue_account:
        user = request.user
        if venue_account.account == user.get_profile()\
                and event.owner == user:
            event.venue_account_owner = venue_account
            event.save()
            success = True
        else:
            error = 'You do not have permission to perform this operation.'
    else:
        error = 'Incorrect parameters.'

    return HttpResponse(json.dumps({'success': success, 'error': error}), mimetype='application/json')


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

    account = Account.objects.get(user_id=event.owner_id)

    if request.method == 'POST':
        form = EditEventForm(account=account, instance=event, data=request.POST)
        if form.is_valid():
            try:
                event_service.save_event(account.user, request.POST, form)
                return HttpResponseRedirect(
                    reverse('event_view', kwargs={'slug': event.slug})
                )

            except:
                form._errors['__all__'] = ErrorList(["Unhandled exception. Please inform administrator."])
    else:
        form = EditEventForm(
            account=account,
            instance=event,
            initial=event_service.prepare_initial_event_data_for_edit(event)
        )

    return render_to_response(template_name, {
            'form': form,
            'event': event
        }, context_instance=RequestContext(request))


@login_required
def copy(request, authentication_key, template_name='events/create/copy_event.html'):
    if request.method == 'POST':
        form = CreateEventForm(account=request.account, data=request.POST, by_admin=request.user.is_staff)
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
            venue_account_owner=basic_event.venue_account_owner
        )

        form = CreateEventForm(
            account=request.account, 
            instance=event, 
            initial=event_service.prepare_initial_event_data_for_copy(basic_event),
            by_admin=request.user.is_staff
        )

    return render_to_response(template_name, {
            'form': form,
            'posting': True
        }, context_instance=RequestContext(request))    


@login_required
def remove(request, authentication_key):
    event_service.remove_event(authentication_key)

    url = request.META.get('HTTP_REFERER', reverse('event_browse'))
    try:
        resolve(url)
    except Resolver404:
        url = reverse('event_browse')

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
        end_time=event.last_occurrence.end_time
    )

    payments_module = request.POST.get("payments_module", "paypal")

    form = SetupFeaturedForm(account, instance=featured_event, initial = {
        "bonus": (0, CAD)
    })

    venue_account_featured_stats = FeaturedEvent.objects.filter(event__venue_id=event.venue.id)    

    if request.method == 'POST':
        form = SetupFeaturedForm(account, instance=featured_event, data=request.POST)

        if form.is_valid():
            featured_event = form.save()

            return process_setup_featured(account, featured_event, request)

    return render_to_response('events/setup_featured_event.html', {
            'form': form,
            'featured_events_stats': venue_account_featured_stats,
            'account': account,
            'payments_module': payments_module
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


def more_events(request, id):
    try:
        target_event = SingleEvent.objects.get(pk=id)
    except SingleEvent.DoesNotExist:
        events = []
    else:
        location_from_user_choice = location_service.LocationFromUserChoice(request)
        events = list(target_event.event.venue_events(location=location_from_user_choice,
                                                      exclude_id=target_event.id))

    content = render_to_string('events/detail_page/similar_events_items.html',
                               {'events': events},
                               context_instance=RequestContext(request))

    return HttpResponse(json.dumps({'success': True,
                                    'content': content,
                                    'count': len(events)}),
                        mimetype='application/json')


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
    search = request.GET.get('search', '')
    locations = location_service.get_autocomplete_locations(search, request.user_location)

    return HttpResponse(json.dumps({
        'locations': locations
    }), mimetype='application/json')


@require_GET
def suggest_cityfusion_venue(request):
    search = request.GET.get("search", "")
    user = request.user

    if search:
        venues = Venue.objects.filter(suggested=True).filter(
            Q(name__icontains=search)|Q(street__icontains=search)|Q(city__name__icontains=search)
        )
    else:
        venues = Venue.objects.filter(suggested=True)

    venues = venues.filter(user=user)[:5]

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

@login_required
def edit_venue(request, venue_id):
    try:
        venue = Venue.objects.get(pk=venue_id, user=request.user, suggested=True)

        return render_to_response('venues/e', context_instance=RequestContext(request))
    except Exception:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp


@login_required
def remove_venue(request, venue_id):
    try:
        venue = Venue.objects.get(pk=venue_id, user=request.user, suggested=True)
        venue_service.delete_venue(venue)

        return HttpResponseRedirect(reverse('userena_profile_detail', kwargs={'username': request.user.username}))
    except Venue.DoesNotExist:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp


def load_model(cls, pk, manager='objects'):
    try:
        model = getattr(cls, manager).get(pk=pk)
    except cls.DoesNotExist:
        model = None

    return model


def get_event_image(request, slug, width, height):
    try:
        event = EventModelDecorator(EventSlug.objects.get(slug=slug).event)
        thumb = event.sized_image(width, height)
        if not thumb:
            thumb_path = '%s/%s' % (settings.STATIC_ROOT, 'images/default-event.jpg')
        else:
            thumb_path = '%s/%s' % (settings.MEDIA_ROOT, thumb)
        image_data = open(thumb_path, 'rb').read()
        mime_type = mimetypes.guess_type(thumb_path)
        return HttpResponse(image_data, mimetype=mime_type)
    except Exception:
        return Http404