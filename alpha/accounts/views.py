# Create your views here.

from models import Account, VenueAccount
from event.models import Event
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from accounts.forms import ReminderSettingsForm, InTheLoopSettingsForm

from django.conf import settings

from django.utils import simplejson as json
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType

from utils import remind_account_about_events, inform_account_about_events_with_tag
from django.contrib.auth.decorators import login_required

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

    tag_name_qs = TAG_MODEL.objects.filter(name__icontains=query, taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(Event)).\
        values_list('name', flat=True).distinct()
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
    # user = request.user
    # account = get_object_or_404(Account, user=user)

    venue_account = VenueAccount.objects.get(slug=slug)

    return render_to_response('venue_accounts/private_venue_account.html', {
                'venue_account': venue_account,
        }, context_instance=RequestContext(request))


def edit_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)

    return render_to_response('venue_accounts/edit_venue_account.html', {
                'venue_account': venue_account,
        }, context_instance=RequestContext(request))


def public_venue_account(request, slug):
    venue_account = VenueAccount.objects.get(slug=slug)

    return render_to_response('venue_accounts/public_venue_account.html', {
                'venue_account': venue_account,
        }, context_instance=RequestContext(request))
