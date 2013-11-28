from accounts.models import VenueAccount


def user_context(request):
    venue_account_id = request.session.get('venue_account_id', False)
    if venue_account_id:
        try:
            current_venue_account = VenueAccount.objects.get(id=venue_account_id)
        except:
            current_venue_account = None

    else:
        current_venue_account = None

    return {
        "current_venue_account": current_venue_account,
        "profile": request.profile
    }


def taxes_context(request):
    account_taxes = []

    if request.account:
        account = request.account
        if not account.not_from_canada:
            account_taxes = account.taxes

    return {
        "account_taxes": account_taxes
    }