# Create your views here.

from models import Account
from event.models import SingleEvent
from django.shortcuts import render_to_response
from django.template import RequestContext


def remind_me(request, single_event_id):
    profile = Account.objects.get(id=request.user.id)
    event = SingleEvent.objects.get(id=single_event_id)

    profile.reminder_events.add(event)

    return render_to_response('accounts/ajax_result_remind_me.html', {
        "event": event
    }, context_instance=RequestContext(request))


def add_in_the_loop(request):
    profile = Account.objects.get(id=request.user.id)
    tags = request.GET.getlist("tag[]")
    profile.in_the_loop_tags.add(*tags)

    return render_to_response('accounts/ajax_result_add_in_the_loop.html', {
        "tags": tags
    }, context_instance=RequestContext(request))
