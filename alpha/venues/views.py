from django.utils import simplejson as json
from django.conf import settings
from accounts.models import VenueAccount, VenueType, Account
from event.models import Event, SingleEvent, FeaturedEvent, Venue
from event.services.featured_service import featured_events_for_region
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from venues.forms import VenueAccountForm, NewVenueAccountForm
from django.contrib.gis.geos import Point
from cities.models import City, Country
from django.db.models import Q
from event.utils import find_nearest_city
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType
from .services import social_links_services, venue_service

MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 10)

TAG_MODEL = getattr(settings, 'TAGGIT_AUTOSUGGEST_MODEL', ('taggit', 'Tag'))
TAG_MODEL = get_model(*TAG_MODEL)

def venues(request):
    current_venue_type = int(request.GET.get("venue_type", 0))

    featured_events = featured_events_for_region(request)

    venue_types = VenueType.active_types.all()

    if current_venue_type:
        venue_accounts = VenueAccount.public_venues.filter(types__id=int(current_venue_type)).order_by("venue__name")
    else:
        venue_accounts = VenueAccount.public_venues.all().order_by("venue__name") # TODO: filter by region

    return render_to_response('venues/index.html', {
        'featured_events': featured_events,
        'venue_accounts': venue_accounts,
        'venue_types': venue_types,
        'current_venue_type': current_venue_type
    }, context_instance=RequestContext(request))


def public_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)

    venue_account.view()

    venue_events = SingleEvent.future_events.filter(event__venue_account_owner=venue_account)
    venue_featured_events = SingleEvent.featured_events.filter(event__venue_account_owner=venue_account)

    tabs_page = "public-venue-account"

    active_tab = request.session.get(tabs_page, "venue-events")

    return render_to_response('venue_accounts/public_venue_account.html', {
                'venue_account': venue_account,
                'venue_events': venue_events,
                'venue_featured_events': venue_featured_events,
                'tabs_page': tabs_page,
                'active_tab': active_tab,
                'private': False
        }, context_instance=RequestContext(request))


@login_required
def private_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)
    
    if venue_account.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

    venue_events = SingleEvent.future_events.filter(event__venue_account_owner=venue_account)
    venue_featured_events = FeaturedEvent.objects.filter(event__venue_account_owner=venue_account)
    venue_archived_events = SingleEvent.archived_events.filter(event__venue_account_owner=venue_account)
    featured_events_stats = FeaturedEvent.objects.filter(event__venue_account_owner=venue_account)

    tabs_page = "private-venue-account"

    active_tab = request.session.get(tabs_page, "venue-events")

    return render_to_response('venue_accounts/private_venue_account.html', {
                'venue_account': venue_account,
                'venue_events': venue_events,
                'venue_featured_events': venue_featured_events,
                'venue_archived_events': venue_archived_events,
                'featured_events_stats': featured_events_stats,
                'tabs_page': tabs_page,
                'active_tab': active_tab,
                'private': True

        }, context_instance=RequestContext(request))


@login_required
def save_venue(request):
    venue_identifier = request.POST["venue_identifier"]
    if venue_identifier:
        return Venue.objects.get(id=int(venue_identifier))

    name = request.POST["venue_name"]
    street = request.POST["street"]
    location = Point((
        float(request.POST["location_lng"]),
        float(request.POST["location_lat"])
    ))

    if request.POST["city_identifier"]:
        city = City.objects.get(id=int(request.POST["city_identifier"]))

    else:
        cities = City.objects.filter(
            Q(name_std=request.POST["geo_city"].encode('utf8')) |
            Q(name=request.POST["geo_city"])
        )

        if cities.count() > 1:
            city = find_nearest_city(location, cities)
        elif not cities.count():
            city = City.objects.distance(location).order_by('distance')[0]
        else:
            city = cities[0]

    country = Country.objects.get(name='Canada')
    venue, created = Venue.objects.get_or_create(name=name, street=street, city=city, country=country, location=location)

    return venue  


@login_required
def create_venue_account(request):
    account = Account.objects.get(user_id=request.user.id)
    form = NewVenueAccountForm()

    venue_account = VenueAccount()

    if request.method == 'POST':
        form = NewVenueAccountForm(data=request.POST)

        if form.is_valid():
            venue = save_venue(request)

            try:
                venue_account = VenueAccount.objects.get(venue=venue)
                return HttpResponseRedirect(reverse('venue_account_already_in_use', args=(venue_account.id, )))

            except:               
                venue_account = VenueAccount(venue=venue, account=account)
                form = NewVenueAccountForm(instance=venue_account, data=request.POST)
                venue_account = form.save()

                if request.POST["picture_src"]:
                    venue_account.picture.name = request.POST["picture_src"].replace(settings.MEDIA_URL, "")

                types = form.cleaned_data['types']
                venue_account.types = types
                venue_account.save()

                return HttpResponseRedirect(reverse('userena_profile_detail', args=(request.user.username, )))                

    return render_to_response('venue_accounts/create_venue_account.html', {
            'venue_account': venue_account,
            'form': form
        }, context_instance=RequestContext(request))


@login_required
def edit_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)

    if venue_account.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

    form = VenueAccountForm(
        instance=venue_account,
        initial={
            "picture_src": "/media/%s" % venue_account.picture,
            "social_links": social_links_services.prepare_social_links(venue_account)
        }
    )

    if request.method == 'POST':
        if request.POST["picture_src"]:
            venue_account.picture.name = request.POST["picture_src"].replace(settings.MEDIA_URL, "")

        form = VenueAccountForm(instance=venue_account, data=request.POST)

        if form.is_valid():
            form.save()
            types = form.cleaned_data['types']
            venue_account.types = types
            return HttpResponseRedirect(reverse('private_venue_account', args=(venue_account.slug, )))

    return render_to_response('venue_accounts/edit_venue_account.html', {
            'venue_account': venue_account,
            'form': form
        }, context_instance=RequestContext(request))    


def venue_account_already_in_use(request, venue_account_id):
    venue_account = VenueAccount.objects.get(id=venue_account_id)

    return render_to_response('venue_accounts/already_in_use.html', {
            'venue_account': venue_account
        }, context_instance=RequestContext(request))


@login_required
def set_venue_privacy(request, venue_account_id, privacy):
    public = (privacy == "public")
    venue_account = VenueAccount.objects.get(id=venue_account_id)
    
    if venue_account.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

    venue_account.public = public
    venue_account.save()

    return HttpResponse(
        "You have made %s venue %s." % (venue_account.venue.name, privacy)
    )


@login_required
def unlink_venue_account_from_user_profile(request):
    success = False
    if request.method == 'POST':
        venue_account_id = request.POST.get('venue_account_id', 0)
        after_action = request.POST.get('after_action', '')
        owner = request.POST.get('owner', '')

        venue_account = VenueAccount.objects.get(id=venue_account_id)
        if venue_account.account.user == request.user:
            venue_service.unlink_venue_account(venue_account, after_action, owner, request.user)
            success = True

    return HttpResponse(json.dumps({'success': success}), mimetype='application/json')


def venue_tags(request):
    """
    Returns a list of JSON objects with a `name` and a `value` property that
    all start like your query string `q` (not case sensitive).
    """
    query = request.GET.get('q', '')
    limit = request.GET.get('limit', MAX_SUGGESTIONS)
    try:
        request.GET.get('limit', MAX_SUGGESTIONS)
        limit = min(int(limit), MAX_SUGGESTIONS)  # max or less
    except ValueError:
        limit = MAX_SUGGESTIONS

    tag_name_qs = TAG_MODEL.objects.filter(
        name__icontains=query,
        taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(VenueAccount)
    ).values_list('name', flat=True).distinct()

    data = [{'name': n, 'value': n} for n in tag_name_qs[:limit]]

    return HttpResponse(json.dumps(data), mimetype='application/json')


def venue_account_tags(request, venue_account_id):
    venue_account = VenueAccount.objects.get(id=venue_account_id)

    return HttpResponse(json.dumps({
        "tags" : [tag.name for tag in venue_account.tags.all()]
    }), mimetype='application/json')
