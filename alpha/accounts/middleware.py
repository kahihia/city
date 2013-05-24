# -*- coding: utf-8 -*-
from models import VenueAccount


class VenueAccountMiddleware(object):
    def process_request(self, request):
        venue_account_id = request.session.get('venue_account_id', False)
        if venue_account_id:
            request.current_venue_account = VenueAccount.objects.get(id=venue_account_id)