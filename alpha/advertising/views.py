from accounts.models import Account
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from advertising.models import AdvertisingCampaign, AdvertisingType
from advertising.forms import AdvertisingSetupForm
from django.contrib import messages


def setup(request):
    profile = Account.objects.get(user_id=request.user.id)
    campaign = AdvertisingCampaign(account=profile)

    form = AdvertisingSetupForm(instance=campaign)

    advertising_types = AdvertisingType.objects.filter(active=True)

    if request.method == 'POST':
        form = AdvertisingSetupForm(instance=campaign, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Advertasing created.')
            return HttpResponseRedirect('/accounts/%s/' % request.user.username)

    return render_to_response('advertising/setup.html', {
        "form": form,
        "advertising_types": advertising_types
    }, context_instance=RequestContext(request))
