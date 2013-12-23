from django.contrib.gis.db import models
from accounts.models import Account, VenueAccount

class VenueAccountTransferring(models.Model):
    target = models.ForeignKey(Account, blank=False, null=False)
    venue_account = models.ForeignKey(VenueAccount, blank=False, null=False)