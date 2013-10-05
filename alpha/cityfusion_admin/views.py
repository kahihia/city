import datetime
import json
from django.contrib.auth.models import User
from cityfusion_admin.models import ReportEvent, ClaimEvent
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from accounts.models import Account
from advertising.models import ShareAdvertisingCampaign
from event.models import Event, FeaturedEvent, FacebookEvent
from event.forms import SetupFeaturedForm, CreateEventForm
from event.services import facebook_services
from cities.models import City, Country
from django_facebook.decorators import facebook_required_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q


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


@staff_member_required
def report_event_list(request):
    reports = ReportEvent.active.all()

    return render_to_response('cf-admin/report_event_list.html', {
                                'reports': reports
                            }, context_instance=RequestContext(request))

@staff_member_required
def report_event_process(request, report_id):
    report = ReportEvent.active.get(id=report_id)
    report.process()

    return HttpResponseRedirect(reverse('report_event_list'))


@staff_member_required
def claim_event_list(request):
    claims = ClaimEvent.active.all()

    return render_to_response('cf-admin/claim_event_list.html', {
                                'claims': claims
                            }, context_instance=RequestContext(request))


@staff_member_required
def import_facebook_events(request):
    form = CreateEventForm(account=request.account, initial={
        "venue_account_owner": request.current_venue_account
    })  # form for manual location choice

    return render_to_response('cf-admin/import_facebook_events.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@staff_member_required
@facebook_required_lazy
def load_facebook_events(request):
    if request.is_ajax():
        try:
            service = facebook_services.FacebookImportService(
                request,
                request.GET['place'],
                request.GET['fb_page_url'])
            data = service.get_events_data(int(request.GET.get('page', 0)))
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
@staff_member_required
def reject_facebook_event(request):
    if request.is_ajax():
        facebook_event_id = request.POST['facebook_event_id']
        FacebookEvent.objects.create(eid=int(facebook_event_id))

        return HttpResponse(json.dumps({'success': True}), mimetype='application/json')
    else:
        raise Http404


@staff_member_required
def clear_facebook_cached_graph(request):
    if 'graph' in request.session:
        request.session.pop('graph')

    return HttpResponse(json.dumps({'success': True}), mimetype='application/json')


@staff_member_required
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

            cities = City.objects.filter(**kwargs)[0:5]

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
        raise Http404
    else:
        raise Http404

@staff_member_required
def user_autocomplete(request):
    if request.is_ajax():
        if request.method == 'GET':
            users = []

            search = request.GET.get('search', '')
            
            users = User.objects.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))[0:10]

            users = [{
                "id": user.id,
                "name": user.username,
            } for user in users]
            return HttpResponse(json.dumps(users), mimetype='application/json')
        raise Http404
    else:
        raise Http404


@staff_member_required
def transfer_event(request, claim_id):
    claim = ClaimEvent.active.get(id=claim_id)
    
    event = claim.event
    user = claim.account.user

    event.venue_account_owner = None
    event.owner = user

    event.save()
    claim.process()

    return HttpResponseRedirect(reverse('claim_event_list'))
    

@staff_member_required
def claim_event_refuse(request, claim_id):
    claim = ClaimEvent.active.get(id=claim_id)
    claim.process()

    return HttpResponseRedirect(reverse('claim_event_list'))


from advertising.models import AdvertisingCampaign, AdvertisingType, Advertising
from advertising.forms import AdvertisingSetupForm, AdvertisingCampaignEditForm
from advertising.utils import get_chosen_advertising_types, get_chosen_advertising_payment_types, get_chosen_advertising_images


@staff_member_required
def admin_advertising(request):
    campaigns = AdvertisingCampaign.objects.order_by("started")
    return render_to_response('cf-admin/admin-advertising-list.html', {
            "campaigns": campaigns
        }, context_instance=RequestContext(request))


@staff_member_required
def admin_advertising_setup(request):
    account = Account.objects.get(user_id=request.user.id)
    campaign = AdvertisingCampaign(account=account, free=True)
    form = AdvertisingSetupForm(account, instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True).order_by("id")

    if request.method == 'POST':
        form = AdvertisingSetupForm(account, instance=campaign, data=request.POST, files=request.FILES)
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


@staff_member_required
def admin_advertising_edit_campaign(request, campaign_id):
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)

    form = AdvertisingCampaignEditForm(campaign.account, instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True).order_by("id")

    advertising_images = { ad.ad_type_id: ad.image for ad in campaign.advertising_set.all() }

    if request.method == 'POST':
        form = AdvertisingCampaignEditForm(campaign.account, instance=campaign, data=request.POST, files=request.FILES)

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


@staff_member_required
def admin_advertising_remove_campaign(request, campaign_id):
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)
    campaign.delete()

    return HttpResponseRedirect(reverse('admin_advertising'))


@staff_member_required
def admin_advertising_remove_ad(request, ad_id):
    ad = Advertising.objects.get(id=ad_id)
    ad.delete()
    return HttpResponseRedirect(reverse('admin_advertising'))


@staff_member_required
def admin_advertising_review(request):
    ads = Advertising.pending.all()

    return render_to_response('cf-admin/admin-advertising-review.html', {
            "ads": ads
        }, context_instance=RequestContext(request))


@staff_member_required
def admin_advertising_change_status(request, ad_id, status):
    ad = Advertising.objects.get(id=ad_id)
    ad.review_status = status
    ad.save()
    return HttpResponseRedirect(reverse('admin_advertising_review'))


@staff_member_required
def admin_featured(request):
    featured_events = FeaturedEvent.objects.order_by('-end_time').all()
    return render_to_response('cf-admin/admin-featured-events.html', {
            "featured_events": featured_events
        }, context_instance=RequestContext(request))


@staff_member_required
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


@staff_member_required
def admin_remove_featured(request, featured_event_id):
    FeaturedEvent.objects.get(id=featured_event_id).delete()
    return HttpResponseRedirect(reverse('admin_featured'))


@staff_member_required
def admin_activate_featured(request, featured_event_id):
    featured_event = FeaturedEvent.objects.get(id=featured_event_id)
    featured_event.active = True
    featured_event.save()
    return HttpResponseRedirect(reverse('admin_featured'))


@staff_member_required
def admin_deactivate_featured(request, featured_event_id):    
    featured_event = FeaturedEvent.objects.get(id=featured_event_id)
    featured_event.active = False
    featured_event.save()
    return HttpResponseRedirect(reverse('admin_featured'))


@staff_member_required
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


@staff_member_required
def free_try(request):
    pass


@staff_member_required
def change_event_owner_search(request):
    events = []
    search = request.REQUEST.get("search", "")
    if search:
        events = Event.future_events.filter(name__icontains=search)

    return render_to_response('cf-admin/event_owner_search.html', {
        'events': events,
        'search': search
    }, context_instance=RequestContext(request))


@require_POST
@staff_member_required
def change_event_owner(request, slug):
    owner_id = request.POST.get("owner_id", None)
    if owner_id:
        event = Event.events.get(slug=slug)
        event.owner = User.objects.get(id=owner_id)
        event.save()

    return HttpResponseRedirect(
        reverse('change_event_owner_search') + "?search=%s" % request.POST.get("search", "")
    )


@staff_member_required
def admin_share_stats(request, campaign_id):
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)
    
    if request.method == 'POST':
        account_id = request.POST.get("account_id")
        
        account = Account.objects.get(id=account_id)

        ShareAdvertisingCampaign.objects.get_or_create(
            account=account,
            campaign=campaign
        )        

        return HttpResponseRedirect(reverse('admin_advertising'))

    return render_to_response('cf-admin/admin-share-stats.html', {
            'campaign': campaign,
            'shared_with': Account.objects.filter(shareadvertisingcampaign__campaign_id=campaign_id)
        }, context_instance=RequestContext(request))

