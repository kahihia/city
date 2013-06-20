# Create your views here.

from models import Account, VenueAccount
from event.models import Event, FeaturedEvent
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils.translation import ugettext as _

from accounts.forms import ReminderSettingsForm, InTheLoopSettingsForm, VenueAccountForm, NewVenueAccountForm

from django.conf import settings

from django.utils import simplejson as json
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType

from utils import remind_account_about_events, inform_account_about_events_with_tag
from django.contrib.auth.decorators import login_required

from userena import settings as userena_settings
from userena.utils import get_profile_model, get_user_model
from userena.views import ExtraContextTemplateView

MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 20)

TAG_MODEL = getattr(settings, 'TAGGIT_AUTOSUGGEST_MODEL', ('taggit', 'Tag'))
TAG_MODEL = get_model(*TAG_MODEL)


def remind_me(request, event_id):
    profile = Account.objects.get(user_id=request.user.id)
    event = Event.future_events.get(id=event_id)

    profile.reminder_events.add(event)

    return render_to_response('accounts/ajax_result_remind_me.html', {
        "event": event
    }, context_instance=RequestContext(request))


def remove_remind_me(request, event_id):
    profile = Account.objects.get(user_id=request.user.id)
    event = Event.future_events.get(id=event_id)
    profile.reminder_events.remove(event)

    return HttpResponseRedirect("/accounts/%s/" % request.user.username)


def add_in_the_loop(request):
    profile = Account.objects.get(user_id=request.user.id)
    tags = request.GET.getlist("tag[]")
    profile.in_the_loop_tags.add(*tags)

    return render_to_response('accounts/ajax_result_add_in_the_loop.html', {
        "tags": tags
    }, context_instance=RequestContext(request))


def reminder_settings(request):
    account = Account.objects.get(user_id=request.user.id)
    form = ReminderSettingsForm(instance=account)
    if request.method == 'POST':
        form = ReminderSettingsForm(instance=account, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder options updated.')
            return HttpResponseRedirect('/accounts/%s/' % request.user.username)

    return render_to_response('accounts/reminder_settings.html', {
        "form": form
    }, context_instance=RequestContext(request))


def in_the_loop_settings(request):
    account = Account.objects.get(user_id=request.user.id)
    form = InTheLoopSettingsForm(instance=account)

    if request.method == 'POST':
        form = InTheLoopSettingsForm(instance=account, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'In the loop options updated.')
            return HttpResponseRedirect('/accounts/%s/' % request.user.username)

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


def remind_preview(request):
    message = remind_account_about_events(
        Account.objects.get(user__email="jaromudr@gmail.com"),
        Event.future_events.all()[0:1]
    )

    return HttpResponse(message)


def in_the_loop_preview(request):
    message = inform_account_about_events_with_tag(
        Account.objects.get(user__email="jaromudr@gmail.com"),
        Event.future_events.all()[0:1],
        {
            "opa": ["Montreal"],
            "hmm": ["Ottava", "Odessa"]
        }
    )

    return HttpResponse(message)


@login_required
def private_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)
    request.session['venue_account_id'] = venue_account.id

    venue_events = Event.future_events.filter(venue=venue_account.venue)
    venue_featured_events = Event.featured_events.filter(venue=venue_account.venue)
    venue_archived_events = Event.archived_events.filter(venue=venue_account.venue)
    featured_events_stats = FeaturedEvent.objects.filter(venue_account=venue_account)

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

    venue_events = Event.future_events.filter(venue=venue_account.venue)
    venue_featured_events = Event.featured_events.filter(venue=venue_account.venue)

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
def create_venue_account(request):
    venue_account = VenueAccount()
    form = VenueAccountForm(
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

    return render_to_response('venue_accounts/create_venue_account.html', {
            'venue_account': venue_account,
            'form': form
        }, context_instance=RequestContext(request))





def set_venue_privacy(request, venue_account_id, privacy):
    public = (privacy == "public")
    venue_account = VenueAccount.objects.get(id=venue_account_id)
    venue_account.public = public
    venue_account.save()

    return HttpResponse(
        "You make %s venue %s" % (venue_account.venue.name, privacy)
    )


def unlink_venue_account_from_user_profile(request, venue_account_id):
    profile = Account.objects.get(user_id=request.user.id)
    venue_account = VenueAccount.objects.get(id=venue_account_id)

    venue_account.accounts.remove(profile)

    return HttpResponseRedirect(
        reverse('userena_profile_detail', args=(request.user.username, ))
    )


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
    extra_context['new_venue_account_form'] = NewVenueAccountForm()
    extra_context['location'] = request.location

    return ExtraContextTemplateView.as_view(
        template_name=template_name,
        extra_context=extra_context
    )(request)
