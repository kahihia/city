import datetime
import json
from cityfusion_admin.models import ReportEvent, ClaimEvent
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from accounts.models import Account
from event.models import Event, FeaturedEvent, FacebookEvent
from event.forms import SetupFeaturedForm, CreateEventForm
from event.services import facebook_service
from cities.models import City, Country
from django.contrib.gis.geos import Point
from django_facebook.decorators import facebook_required


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


@facebook_required
def import_facebook_events(request):
    form = CreateEventForm(account=request.account, initial={
        "venue_account_owner": request.current_venue_account
    })  # form for manual location choice

    return render_to_response('cf-admin/import_facebook_events.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def load_facebook_events(request):
    if request.is_ajax():
        try:
            data = facebook_service.get_facebook_events_data(
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


def location_autocomplete(request):
    if request.is_ajax():
        if request.method == 'GET':
            canada = Country.objects.get(name='Canada')

            locations = []

            kwargs = {
                'country': canada
            }

            search = request.GET.get('search', '')

            if search:
                kwargs['name__icontains'] = search

            cities = City.objects.filter(**kwargs)

            if request.user_location:
                cities = cities.distance(Point(request.user_location['location'])).order_by('-distance')

            cities = cities[0:5]

            for city in cities:
                if city.region:
                    name = '%s, %s, %s' % (city.name, city.region.name, city.country.name)
                else:
                    name = '%s, %s' % (city.name, city.country.name)
                locations.append({
                    'id': city.id,
                    'name': name,
                    'city_name': city.name
                })

            return HttpResponse(json.dumps(locations), mimetype='application/json')
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


from advertising.models import AdvertisingCampaign, AdvertisingType, Advertising
from advertising.forms import AdvertisingSetupForm, AdvertisingCampaignEditForm
from advertising.utils import get_chosen_advertising_types, get_chosen_advertising_payment_types, get_chosen_advertising_images

def admin_advertising(request):
    campaigns = AdvertisingCampaign.admin.all()
    return render_to_response('cf-admin/admin-advertising-list.html', {
            "campaigns": campaigns
        }, context_instance=RequestContext(request))

def admin_advertising_setup(request):
    account = Account.objects.get(user_id=request.user.id)
    campaign = AdvertisingCampaign(account=account, owned_by_admin=True)
    form = AdvertisingSetupForm(instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True).order_by("id")

    if request.method == 'POST':
        form = AdvertisingSetupForm(instance=campaign, data=request.POST, files=request.FILES)
        if form.is_valid():
            advertising_campaign = form.save()

            chosen_advertising_types = get_chosen_advertising_types(campaign, request)
            chosen_advertising_payment_types = get_chosen_advertising_payment_types(campaign, request)
            chosen_advertising_images = get_chosen_advertising_images(campaign, request)

            for advertising_type_id in chosen_advertising_types:
                advertising_type = AdvertisingType.objects.get(id=advertising_type_id)
                advertising = Advertising(
                    ad_type=advertising_type,
                    campaign=advertising_campaign,
                    payment_type=chosen_advertising_payment_types[advertising_type_id],
                    image=chosen_advertising_images[advertising_type_id],
                    cpm_price=advertising_type.cpm_price,
                    cpc_price=advertising_type.cpc_price,
                    review_status="ACCEPTED"
                )

                advertising.save()            

            return HttpResponseRedirect(reverse('admin_advertising'))

    chosen_advertising_types = get_chosen_advertising_types(campaign, request)
    chosen_advertising_payment_types = get_chosen_advertising_payment_types(campaign, request)
    chosen_advertising_images = get_chosen_advertising_images(campaign, request)

    return render_to_response('cf-admin/admin-advertising-setup.html', {
        "form": form,
        "advertising_types": advertising_types,
        "chosen_advertising_types": chosen_advertising_types,
        "chosen_advertising_payment_types": chosen_advertising_payment_types,
        "chosen_advertising_images": chosen_advertising_images

    }, context_instance=RequestContext(request))


def admin_advertising_edit_campaign(request, campaign_id):
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)

    form = AdvertisingCampaignEditForm(instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True).order_by("id")

    advertising_images = { ad.ad_type_id: ad.image for ad in campaign.advertising_set.all() }

    if request.method == 'POST':
        form = AdvertisingCampaignEditForm(instance=campaign, data=request.POST, files=request.FILES)

        if form.is_valid():
            campaign = form.save()

            chosen_advertising_types = get_chosen_advertising_types(campaign, request)
            chosen_advertising_payment_types = get_chosen_advertising_payment_types(campaign, request)
            chosen_advertising_images = get_chosen_advertising_images(campaign, request)

            # Remove unchecked ads
            for ad in campaign.advertising_set.all():
                if ad.ad_type_id not in chosen_advertising_types:
                    ad.delete()

            # Create or update ads                    
            for advertising_type_id in chosen_advertising_types:
                advertising_type = AdvertisingType.objects.get(id=advertising_type_id)
                advertising, created = Advertising.objects.get_or_create(
                    ad_type=advertising_type,
                    campaign=campaign
                )

                advertising.payment_type=chosen_advertising_payment_types[advertising_type_id]

                if advertising_type_id in chosen_advertising_images:
                    advertising.image=chosen_advertising_images[advertising_type_id]

                advertising.cpm_price=advertising_type.cpm_price
                advertising.cpc_price=advertising_type.cpc_price

                advertising.save()                    

            campaign = form.save()
            return HttpResponseRedirect(reverse('admin_advertising'))

    chosen_advertising_types = get_chosen_advertising_types(campaign, request)
    chosen_advertising_payment_types = get_chosen_advertising_payment_types(campaign, request)
    chosen_advertising_images = get_chosen_advertising_images(campaign, request)        

    return render_to_response('cf-admin/admin-advertising-edit.html', {
        "campaign": campaign,
        "form": form,
        "advertising_types": advertising_types,
        "advertising_images": advertising_images,
        "chosen_advertising_types": chosen_advertising_types,
        "chosen_advertising_payment_types": chosen_advertising_payment_types,
        "chosen_advertising_images": chosen_advertising_images
    }, context_instance=RequestContext(request))


def admin_advertising_remove_campaign(request, campaign_id):
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)
    campaign.delete()

    return HttpResponseRedirect(reverse('admin_advertising'))

def admin_advertising_remove_ad(request, ad_id):
    ad = Advertising.objects.get(id=ad_id)
    ad.delete()
    return HttpResponseRedirect(reverse('admin_advertising'))

def admin_advertising_review(request):
    ads = Advertising.pending.all()

    return render_to_response('cf-admin/admin-advertising-review.html', {
            "ads": ads
        }, context_instance=RequestContext(request))

def admin_advertising_change_status(request, ad_id, status):
    ad = Advertising.objects.get(id=ad_id)
    ad.review_status = status
    ad.save()
    return HttpResponseRedirect(reverse('admin_advertising_review'))



def admin_featured(request):
    featured_events = FeaturedEvent.future.all()
    return render_to_response('cf-admin/admin-featured-events.html', {
            "featured_events": featured_events
        }, context_instance=RequestContext(request))

def admin_setup_featured(request, event_id):
    account = request.account
    event = Event.events.get(id=event_id)    

    featured_event = FeaturedEvent(
        event=event,
        owner=account,
        start_time=datetime.date.today(),
        end_time=datetime.date.today() + datetime.timedelta(days=15),
        active=True,
        owned_by_admin=True
    )

    form = SetupFeaturedForm(
        instance=featured_event
    )

    if request.method == 'POST':
        form = SetupFeaturedForm(instance=featured_event, data=request.POST)

        if form.is_valid():
            featured_event = form.save()

            return HttpResponseRedirect(reverse('admin_featured'))

    return render_to_response('cf-admin/admin-setup-featured-event.html', {
            'form': form,
            'event': event
        }, context_instance=RequestContext(request))

def admin_remove_featured(request, featured_event_id):
    FeaturedEvent.objects.get(id=featured_event_id).delete()
    return HttpResponseRedirect(reverse('admin_featured'))

def admin_activate_featured(request, featured_event_id):
    featured_event = FeaturedEvent.objects.get(id=featured_event_id)
    featured_event.active = True
    featured_event.save()
    return HttpResponseRedirect(reverse('admin_featured'))

def admin_deactivate_featured(request, featured_event_id):    
    featured_event = FeaturedEvent.objects.get(id=featured_event_id)
    featured_event.active = False
    featured_event.save()
    return HttpResponseRedirect(reverse('admin_featured'))

def admin_edit_featured(request, featured_event_id):
    featured_event = FeaturedEvent.objects.get(id=featured_event_id)
    form = SetupFeaturedForm(
        instance=featured_event
    )
    
    if request.method == 'POST':
        form = SetupFeaturedForm(instance=featured_event, data=request.POST)

        if form.is_valid():
            featured_event = form.save()

            return HttpResponseRedirect(reverse('admin_featured'))

    return render_to_response('cf-admin/admin-setup-featured-event.html', {
            'form': form,
            'event': featured_event.event
        }, context_instance=RequestContext(request))

def free_try(request):
    pass
