from accounts.models import Account
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from advertising.models import AdvertisingCampaign, AdvertisingType, Advertising
from advertising.forms import AdvertisingSetupForm
from django.contrib import messages
from advertising.utils import parse_advertisings_data_from_request


def open(request, advertising_id):
    advertising = get_object_or_404(Advertising, pk=advertising_id)

    advertising.click()

    return HttpResponseRedirect(advertising.campaign.website)


def setup(request):
    profile = Account.objects.get(user_id=request.user.id)
    campaign = AdvertisingCampaign(account=profile)

    form = AdvertisingSetupForm(instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True).order_by("id")

    if request.method == 'POST':
        form = AdvertisingSetupForm(instance=campaign, data=request.POST, files=request.FILES)
        if form.is_valid():
            advertising_campaign = form.save()

            chosen_advertising_types, chosen_advertising_payment_types, chosen_advertising_images = parse_advertisings_data_from_request(request)

            for advertising_type_id in chosen_advertising_types:
                advertising = Advertising(
                    ad_type=AdvertisingType.objects.get(id=advertising_type_id),
                    campaign=advertising_campaign,
                    payment_type=chosen_advertising_payment_types[advertising_type_id],
                    image=chosen_advertising_images[advertising_type_id]
                )

                advertising.save()

            messages.success(request, 'Advertising created.')

            return HttpResponseRedirect('/accounts/%s/' % request.user.username)

    chosen_advertising_types, chosen_advertising_payment_types, chosen_advertising_images = parse_advertisings_data_from_request(request)

    return render_to_response('advertising/setup.html', {
        "form": form,
        "advertising_types": advertising_types,
        "chosen_advertising_types": chosen_advertising_types,
        "chosen_advertising_payment_types": chosen_advertising_payment_types,
        "chosen_advertising_images": chosen_advertising_images

    }, context_instance=RequestContext(request))
