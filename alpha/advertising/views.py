from accounts.models import Account
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from advertising.models import AdvertisingCampaign, AdvertisingType, Advertising, AdvertisingOrder
from advertising.forms import PaidAdvertisingSetupForm, AdvertisingCampaignEditForm, DepositFundsForCampaignForm
from advertising.utils import get_chosen_advertising_types, get_chosen_advertising_payment_types, get_chosen_advertising_images

from django.contrib.auth.decorators import login_required
from accounts.decorators import native_region_required
from decimal import Decimal


def open(request, advertising_id):
    advertising = get_object_or_404(Advertising, pk=advertising_id)

    advertising.click()

    return HttpResponseRedirect(advertising.campaign.website)


@login_required
@native_region_required(why_message="native_region_required")
def setup(request):
    account = Account.objects.get(user_id=request.user.id)
    campaign = AdvertisingCampaign(account=account, venue_account=request.current_venue_account)

    form = PaidAdvertisingSetupForm(account, instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True).order_by("id")

    if request.method == 'POST':
        form = PaidAdvertisingSetupForm(account, instance=campaign, data=request.POST, files=request.FILES)
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
                    cpc_price=advertising_type.cpc_price
                )

                advertising.save()

            budget = Decimal(request.POST["order_budget"])
            total_price = budget

            for tax in account.taxes():
                total_price = total_price + (budget * tax.tax)

            order = AdvertisingOrder(
                budget=budget,
                total_price=total_price,
                campaign=advertising_campaign,
                account=account
            )

            order.save()

            return HttpResponseRedirect(reverse('advertising_payment', args=(str(order.id),)))

    chosen_advertising_types = get_chosen_advertising_types(campaign, request)
    chosen_advertising_payment_types = get_chosen_advertising_payment_types(campaign, request)
    chosen_advertising_images = get_chosen_advertising_images(campaign, request)

    return render_to_response('advertising/setup.html', {
        "form": form,
        "advertising_types": advertising_types,
        "chosen_advertising_types": chosen_advertising_types,
        "chosen_advertising_payment_types": chosen_advertising_payment_types,
        "chosen_advertising_images": chosen_advertising_images

    }, context_instance=RequestContext(request))


@login_required
@native_region_required(why_message="native_region_required")
def deposit_funds_for_campaign(request, campaign_id):
    account = Account.objects.get(user_id=request.user.id)    
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)

    if campaign.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

    form = DepositFundsForCampaignForm()

    if request.method == 'POST':
        form = DepositFundsForCampaignForm(data=request.POST)
        if form.is_valid():
            budget = Decimal(request.POST["order_budget"])
            total_price = budget

            for tax in account.taxes():
                total_price = total_price + (budget * tax.tax)

            order = AdvertisingOrder(
                budget=budget,
                total_price=total_price,
                campaign=campaign,
                account=account
            )
            order.save()

            return HttpResponseRedirect(reverse('advertising_payment', args=(str(order.id),)))

    return render_to_response('advertising/campaign/deposit_funds.html', {
        "campaign": campaign,
        "form": form
    }, context_instance=RequestContext(request))

def edit_campaign(request, campaign_id):
    account = Account.objects.get(user_id=request.user.id)
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)

    if campaign.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

    form = AdvertisingCampaignEditForm(account, instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True).order_by("id")

    advertising_images = { ad.ad_type_id: ad.image for ad in campaign.advertising_set.all() }

    if request.method == 'POST':
        form = AdvertisingCampaignEditForm(account, instance=campaign, data=request.POST, files=request.FILES)

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
            return HttpResponseRedirect('/accounts/%s/' % request.user.username)

    chosen_advertising_types = get_chosen_advertising_types(campaign, request)
    chosen_advertising_payment_types = get_chosen_advertising_payment_types(campaign, request)
    chosen_advertising_images = get_chosen_advertising_images(campaign, request)        

    return render_to_response('advertising/campaign/edit.html', {
        "campaign": campaign,
        "form": form,
        "advertising_types": advertising_types,
        "advertising_images": advertising_images,
        "chosen_advertising_types": chosen_advertising_types,
        "chosen_advertising_payment_types": chosen_advertising_payment_types,
        "chosen_advertising_images": chosen_advertising_images
    }, context_instance=RequestContext(request))


def remove_campaign(request, campaign_id):
    campaign = AdvertisingCampaign.objects.get(id=campaign_id)    

    if campaign.account.user != request.user:
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

    campaign.delete()

    return HttpResponseRedirect('/accounts/%s/' % request.user.username)


def payment(request, order_id):
    order = get_object_or_404(AdvertisingOrder, pk=order_id)

    # form = PaypalConfirmationForm()

    return render_to_response('advertising/payment.html', {
        "order": order
    }, context_instance=RequestContext(request))

def advertising_order(request, order_id):
    order = get_object_or_404(AdvertisingOrder, pk=order_id)
    payment = order.payment_set.all()[0]

    # form = PaypalConfirmationForm()

    return render_to_response('advertising/order.html', {
        "order": order,
        "payment": payment
    }, context_instance=RequestContext(request))    
