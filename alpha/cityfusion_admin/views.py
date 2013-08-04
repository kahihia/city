import json
from cityfusion_admin.models import ReportEvent, ClaimEvent
from cityfusion_admin.utils import get_facebook_events_data
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from event.models import Event, FacebookEvent
from accounts.models import Account


@require_POST
def report_event(request):
    report = ReportEvent(
        event_id=request.POST["event_id"],
        message=request.POST["message"]
    )
    if "account_id" in request.POST:
        report.account_id = request.POST["account_id"]

    report.save()


    return HttpResponse(json.dumps({
        "answer": "OK",
        "id": report.id 
    }), mimetype="application/json")


@require_POST
def claim_event(request):
    claim = ClaimEvent(
        event_id=request.POST["event_id"],
        account_id=request.POST["account_id"],
        message=request.POST["message"]
    )

    claim.save()

    return HttpResponse(json.dumps({
        "answer": "OK",
        "id": claim.id
    }), mimetype="application/json")


def report_event_list(request):
    reports = ReportEvent.active.all()

    return render_to_response('cf-admin/report_event_list.html', {
                                'reports': reports
                            }, context_instance=RequestContext(request))

def report_event_process(request, report_id):
    report = ReportEvent.active.get(id=report_id)
    report.process()

    return HttpResponseRedirect(reverse('report_event_list'))


def claim_event_list(request):
    claims = ClaimEvent.active.all()

    return render_to_response('cf-admin/claim_event_list.html', {
                                'claims': claims
                            }, context_instance=RequestContext(request))


def import_facebook_events(request):
    return render_to_response('cf-admin/import_facebook_events.html',
                              context_instance=RequestContext(request))


def load_facebook_events(request):
    if request.is_ajax():
        try:
            data = get_facebook_events_data(
                request,
                request.GET['place'],
                int(request.GET.get('page', 0))
            )

            content = render_to_string('cf-admin/facebook_event_list.html',
                                       {'events': data['events']},
                                       context_instance=RequestContext(request))
            response = {
                'success': True,
                'content': content,
                'page': data['page']
            }
        except Exception as e:
            response = {
                'success': False,
                'text': e.message
            }

        return HttpResponse(json.dumps(response), mimetype='application/json')
    else:
        raise Http404


@require_POST
def reject_facebook_event(request):
    if request.is_ajax():
        facebook_event_id = request.POST['facebook_event_id']
        FacebookEvent.objects.create(eid=int(facebook_event_id))

        return HttpResponse(json.dumps({'success': True}), mimetype='application/json')
    else:
        raise Http404


def transfer_event(request, claim_id):
    claim = ClaimEvent.active.get(id=claim_id)
    
    event = claim.event
    user = claim.account.user

    event.venue_account_owner = None
    event.owner = user

    event.save()
    claim.process()

    return HttpResponseRedirect(reverse('claim_event_list'))
    

def claim_event_refuse(request, claim_id):
    claim = ClaimEvent.active.get(id=claim_id)
    claim.process()

    return HttpResponseRedirect(reverse('claim_event_list'))