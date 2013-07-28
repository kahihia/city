import json
from cityfusion_admin.models import ReportEvent, ClaimEvent
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from event.models import Event
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