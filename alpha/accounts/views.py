# Create your views here.

from models import Account
from event.models import SingleEvent, Event
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from accounts.forms import ReminderSettingsForm, InTheLoopSettingsForm

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson as json
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType

from django.core.mail.message import EmailMessage

from utils import remind_account_about_events

MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 20)

TAG_MODEL = getattr(settings, 'TAGGIT_AUTOSUGGEST_MODEL', ('taggit', 'Tag'))
TAG_MODEL = get_model(*TAG_MODEL)


def remind_me(request, single_event_id):
    profile = Account.objects.get(user_id=request.user.id)
    event = SingleEvent.objects.get(id=single_event_id)

    profile.reminder_events.add(event)

    return render_to_response('accounts/ajax_result_remind_me.html', {
        "event": event
    }, context_instance=RequestContext(request))


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
        SingleEvent.future_events.all().select_related('event')[0:1]
    )

    return HttpResponse(message)


def in_the_loop_preview(request):
    featured_events = SingleEvent.featured_events.all().select_related('event')[:4]

    events = SingleEvent.future_events.all() \
        .select_related('event')[0:5]

    similar_events = SingleEvent.future_events.all() \
        .select_related('event')[0:10]

    return render_to_response('accounts/in_the_loop_email.html', {
        "featured_events": featured_events,
        "events": events,
        "similar_events": similar_events,
        "tag": "Aboriginal",
        "tcu_place": "Saskatoon"
    }, context_instance=RequestContext(request))