def get_chosen_advertising_types(campaign, request):
    if "advertising_types" in request.POST:
        return map(lambda x: int(x), request.POST.getlist("advertising_types"))
    else:
        return map(lambda x: int(x), campaign.advertising_set.values_list('ad_type_id', flat=True))


def get_chosen_advertising_payment_types(campaign, request):
    chosen_advertising_payment_types = { int(key.split(".")[1]): value for key, value in request.POST.iteritems() if key.startswith("advertising_payment_type") }
    if chosen_advertising_payment_types:
        return chosen_advertising_payment_types
    else:
        return { ad.ad_type_id: ad.payment_type for ad in campaign.advertising_set.all() }


def get_chosen_advertising_images(campaign, request):    
    chosen_advertising_images =  { int(key.split(".")[1]): value for key, value in request.FILES.iteritems() if key.startswith("advertising_image") }
    if chosen_advertising_images:
        return chosen_advertising_images        
    else:
        return {}

