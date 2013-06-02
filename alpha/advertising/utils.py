def parse_advertisings_data_from_request(request):
    chosen_advertising_types = map(lambda x: int(x), request.POST.getlist("advertising_types"))
    chosen_advertising_payment_types = { int(key.split(".")[1]): value for key, value in request.POST.iteritems() if key.startswith("advertising_payment_type") }
    chosen_advertising_images = { int(key.split(".")[1]): value for key, value in request.FILES.iteritems() if key.startswith("advertising_image") }

    return (
        chosen_advertising_types,
        chosen_advertising_payment_types,
        chosen_advertising_images
    )
