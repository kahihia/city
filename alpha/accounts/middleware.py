# -*- coding: utf-8 -*-
from models import VenueAccount, Account


class VenueAccountMiddleware(object):
    def process_request(self, request):
        venue_account_id = request.session.get('venue_account_id', False)
        if venue_account_id:
            request.current_venue_account = VenueAccount.objects.get(id=venue_account_id)


class UserProfileMiddleware(object):
    def process_request(self, request):
        if request.user.id:
            request.profile = Account.objects.get(user_id=request.user.id)

