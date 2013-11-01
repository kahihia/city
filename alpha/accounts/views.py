# Create your views here.

from pdfutils.reports import Report

from models import Account, VenueAccount
from event.models import Event, SingleEvent, FeaturedEvent, Venue, EventTransferring
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils.translation import ugettext as _

from accounts.forms import ReminderSettingsForm, InTheLoopSettingsForm, VenueAccountForm, NewVenueAccountForm

from django.conf import settings

from django.utils import simplejson as json
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType

from utils import remind_account_about_events, inform_account_about_events_with_tags
from django.contrib.auth.decorators import login_required
from accounts.decorators import ajax_login_required

from userena import settings as userena_settings
from userena.utils import get_profile_model, get_user_model
from userena.views import ExtraContextTemplateView

from django.contrib.gis.geos import Point
from cities.models import City, Country
from django.db.models import Q
from event.utils import find_nearest_city
from advertising.models import AdvertisingOrder
from event.models import FeaturedEventOrder
from accounts.forms import AccountForm
from userena.decorators import secure_required
from guardian.decorators import permission_required_or_403

import re


MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 10)

TAG_MODEL = getattr(settings, 'TAGGIT_AUTOSUGGEST_MODEL', ('taggit', 'Tag'))
TAG_MODEL = get_model(*TAG_MODEL)


@ajax_login_required
def remind_me(request, single_event_id):
    profile = Account.objects.get(user_id=request.user.id)
    single_event = SingleEvent.future_events.get(id=single_event_id)
    profile.reminder_single_events.add(single_event)

    return HttpResponse(json.dumps({
        "id": single_event.id,
        "name": single_event.name
    }), mimetype='application/json')


@login_required
def remove_remind_me(request, single_event_id):
    profile = Account.objects.get(user_id=request.user.id)
    single_event = SingleEvent.future_events.get(id=single_event_id)
    profile.reminder_single_events.remove(single_event)

    return HttpResponseRedirect(reverse('userena_profile_detail', kwargs={'username': request.user.username}))


@ajax_login_required
def add_in_the_loop(request):
    profile = Account.objects.get(user_id=request.user.id)
    tags = request.GET.getlist("tag[]")
    profile.in_the_loop_tags.add(*tags)

    return HttpResponse(json.dumps({
        "tags": tags
    }), mimetype='application/json')


@login_required
def reminder_settings(request):
    account = Account.objects.get(user_id=request.user.id)
    form = ReminderSettingsForm(instance=account)
    if request.method == 'POST':
        form = ReminderSettingsForm(instance=account, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder options updated.')
            return HttpResponseRedirect(reverse('userena_profile_detail', kwargs={'username': request.user.username}))

    return render_to_response('accounts/reminder_settings.html', {
        "form": form
    }, context_instance=RequestContext(request))

@login_required
def in_the_loop_settings(request):
    account = Account.objects.get(user_id=request.user.id)
    form = InTheLoopSettingsForm(instance=account)

    if request.method == 'POST':
        form = InTheLoopSettingsForm(instance=account, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'In the loop options updated.')
            return HttpResponseRedirect(reverse('userena_profile_detail', kwargs={'username': request.user.username}))

    return render_to_response('accounts/in_the_loop_settings.html', {
        "form": form
    }, context_instance=RequestContext(request))


def in_the_loop_tags(request):
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
        taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(Event)
    ).values_list('name', flat=True).distinct()

    data = [{'name': n, 'value': n} for n in tag_name_qs[:limit]]

    return HttpResponse(json.dumps(data), mimetype='application/json')

def cities_autosuggest(request):
    query = request.GET.get('q', '')
    limit = request.GET.get('limit', MAX_SUGGESTIONS)
    try:
        request.GET.get('limit', MAX_SUGGESTIONS)
        limit = min(int(limit), MAX_SUGGESTIONS)  # max or less
    except ValueError:
        limit = MAX_SUGGESTIONS

    cities = City.objects.filter(
        name__icontains=query
    )

    data = [{'name': city.__unicode__(), 'value': str(city.id) } for city in cities[:limit]]

    return HttpResponse(json.dumps(data), mimetype='application/json')


def remind_preview(request):
    message = remind_account_about_events(
        Account.objects.get(user__email="jaromudr@gmail.com"),
        SingleEvent.future_events.all()[0:1]
    )

    return HttpResponse(message)


def in_the_loop_preview(request):
    message = inform_account_about_events_with_tags(
        Account.objects.get(user__email="jaromudr@gmail.com")
    )

    return HttpResponse(message)


@login_required
def private_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)
    
    if venue_account.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp


    venue_events = SingleEvent.future_events.filter(event__venue_account_owner=venue_account)
    # venue_featured_events = SingleEvent.featured_events.filter(event__venue_account_owner=venue_account)
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


def public_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)

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

                types = form.cleaned_data['types']
                venue_account.types = types
                venue_account.save()

                return HttpResponseRedirect(reverse('userena_profile_detail', args=(request.user.username, )))                

    return render_to_response('venue_accounts/create_venue_account.html', {
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
        "You make %s venue %s" % (venue_account.venue.name, privacy)
    )


@login_required
def unlink_venue_account_from_user_profile(request, venue_account_id):
    venue_account = VenueAccount.objects.get(id=venue_account_id)
    
    if venue_account.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

    venue_account.delete()

    return HttpResponseRedirect(
        reverse('userena_profile_detail', args=(request.user.username, ))
    )


@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def profile_detail(request, username, template_name=userena_settings.USERENA_PROFILE_DETAIL_TEMPLATE, extra_context=None, **kwargs):
    """
    Detailed view of an user.

    :param username:
        String of the username of which the profile should be viewed.

    :param template_name:
        String representing the template name that should be used to display
        the profile.

    :param extra_context:
        Dictionary of variables which should be supplied to the template. The
        ``profile`` key is always the current profile.

    **Context**

    ``profile``
        Instance of the currently viewed ``Profile``.

    """
    user = get_object_or_404(get_user_model(),
                             username__iexact=username)

    profile_model = get_profile_model()
    try:
        profile = user.get_profile()
    except profile_model.DoesNotExist:
        profile = profile_model.objects.create(user=user)

    if not profile.can_view_profile(request.user):
        return HttpResponseForbidden(_("You don't have permission to view this profile."))
    if not extra_context:
        extra_context = dict()
    
    extra_context['profile'] = user.get_profile()
    extra_context['hide_email'] = userena_settings.USERENA_HIDE_EMAIL
    extra_context['location'] = request.user_location["user_location_lat_lon"]
    extra_context['is_admin'] = user.is_superuser
    extra_context['per_page'] = int(request.GET.get('per_page', 6))

    tabs_page = "profile-detail"
    active_tab = request.session.get(tabs_page, "account-events")
    extra_context['active_tab'] = active_tab

    return ExtraContextTemplateView.as_view(
        template_name=template_name,
        extra_context=extra_context
    )(request)    


@login_required
def orders(request):
    account = Account.objects.get(user_id=request.user.id)

    advertising_orders = AdvertisingOrder.objects.filter(campaign__account_id=account.id)
    featured_orders = FeaturedEventOrder.objects.filter(featured_event__owner_id=account.id)

    tabs_page = 'orders'
    active_tab = request.session.get(tabs_page, 'advertising')

    return render_to_response('accounts/orders.html', {
            'account': account,
            'advertising_orders': advertising_orders,
            'featured_orders': featured_orders,
            'tabs_page': tabs_page,
            'active_tab': active_tab
        }, context_instance=RequestContext(request))


@login_required
def order_advertising_printed(request, order_id):
    order = AdvertisingOrder.objects.get(pk=order_id)
    return render_to_response('accounts/order_printed.html',
                              {'order': order,
                               'user': order.account.user},
                              context_instance=RequestContext(request))


@login_required
def order_featured_printed(request, order_id):
    order = FeaturedEventOrder.objects.get(pk=order_id)
    return render_to_response('accounts/order_printed.html',
                              {'order': order,
                               'user': order.account.user},
                              context_instance=RequestContext(request))


class OrderAdvertisingPdf(Report):
    title = 'Invoice'
    template_name = 'accounts/order_printed.html'
    slug = 'order-report'
    orientation = 'portrait'

    def get_styles(self):
        self.styles = ['styles/orders/printed.css']
        return super(OrderAdvertisingPdf, self).get_styles()

    def get_context_data(self):
        order = AdvertisingOrder.objects.get(pk=self.kwargs['order_id'])

        context = super(OrderAdvertisingPdf, self).get_context_data()
        context['order'] = order
        context['user'] = order.account.user
        return context

    def get(self, request, **kwargs):
        return self.render()


class OrderFeaturedPdf(Report):
    title = 'Invoice'
    template_name = 'accounts/order_printed.html'
    slug = 'order-report'
    orientation = 'portrait'

    def get_styles(self):
        self.styles = ['styles/orders/printed.css']
        return super(OrderFeaturedPdf, self).get_styles()

    def get_context_data(self):
        order = FeaturedEventOrder.objects.get(pk=self.kwargs['order_id'])

        context = super(OrderFeaturedPdf, self).get_context_data()
        context['order'] = order
        context['user'] = order.account.user
        return context

    def get(self, request, **kwargs):
        return self.render()


@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def profile_edit(request, username, edit_profile_form=AccountForm,
                 template_name='userena/profile_form.html', success_url=None, why_message=None, 
                 extra_context=None, **kwargs):
    """
    Edit profile.

    Edits a profile selected by the supplied username. First checks
    permissions if the user is allowed to edit this profile, if denied will
    show a 404. When the profile is successfully edited will redirect to
    ``success_url``.

    :param username:
        Username of the user which profile should be edited.

    :param edit_profile_form:

        Form that is used to edit the profile. The :func:`EditProfileForm.save`
        method of this form will be called when the form
        :func:`EditProfileForm.is_valid`.  Defaults to :class:`EditProfileForm`
        from userena.

    :param template_name:
        String of the template that is used to render this view. Defaults to
        ``userena/edit_profile_form.html``.

    :param success_url:
        Named URL which will be passed on to a django ``reverse`` function after
        the form is successfully saved. Defaults to the ``userena_detail`` url.

    :param extra_context:
        Dictionary containing variables that are passed on to the
        ``template_name`` template.  ``form`` key will always be the form used
        to edit the profile, and the ``profile`` key is always the edited
        profile.

    **Context**

    ``form``
        Form that is used to alter the profile.

    ``profile``
        Instance of the ``Profile`` that is edited.

    """
    user = get_object_or_404(get_user_model(),
                             username__iexact=username)

    profile = user.get_profile()

    user_initial = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'not_from_canada': profile.not_from_canada or not request.user_location['is_canada'],
        'native_region': profile.native_region or request.user_location['user_location_region']
    }

    form = edit_profile_form(instance=profile, initial=user_initial)

    if request.method == 'POST':
        form = edit_profile_form(request.POST, request.FILES, instance=profile,
                                 initial=user_initial)

        if form.is_valid():
            profile = form.save()

            if profile.not_from_canada or profile.native_region:
                profile.tax_origin_confirmed = True
            else:
                profile.tax_origin_confirmed = False
            profile.save()

            if success_url: 
                redirect_to = success_url
                # Fix strange bug on production
                redirect_to = re.sub(r'http:\/([^\/])', r'http://\1', redirect_to)
            else: 
                redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['profile'] = profile
    extra_context['why_message'] = why_message


    return ExtraContextTemplateView.as_view(template_name=template_name,
                                            extra_context=extra_context)(request)


def set_context(request, context="root"):
    if context=="root":
        request.session['venue_account_id'] = None
    else:
        venue_account = VenueAccount.objects.get(slug=context)
        request.session['venue_account_id'] = venue_account.id

    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))


def redirect_to_active_user_context(request):
    venue_account_id = request.session.get('venue_account_id', None)

    if venue_account_id:
        venue_account = VenueAccount.objects.get(id=venue_account_id)
        return HttpResponseRedirect(reverse('private_venue_account', args=(venue_account.slug, )))

    else:
        return HttpResponseRedirect(reverse('userena_profile_detail', kwargs={'username': request.user.username}))


@login_required
def clear_facebook_cached_graph(request):
    if 'graph' in request.session:
        request.session.pop('graph')

    return HttpResponse(json.dumps({'success': True}), mimetype='application/json')


@login_required
def accept_transferring(request, transferring_id):
    success = False
    try:
        transferring = EventTransferring.objects.get(pk=transferring_id)
    except EventTransferring.DoesNotExist:
        transferring = None

    if transferring and transferring.target:
        for event in transferring.events.all():
            event.owner = transferring.target
            event.save()

            transferring.events.remove(event)

        transferring.delete()
        success = True

    return HttpResponse(json.dumps({'success': success}), mimetype='application/json')


@login_required
def reject_transferring(request, transferring_id):
    success = False
    try:
        transferring = EventTransferring.objects.get(pk=transferring_id)
    except EventTransferring.DoesNotExist:
        transferring = None

    if transferring and transferring.target:
        for event in transferring.events.all():
            transferring.events.remove(event)

        transferring.delete()
        success = True

    return HttpResponse(json.dumps({'success': success}), mimetype='application/json')