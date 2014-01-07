from django.contrib.gis.db import models


class VenueAccountTransferring(models.Model):
    target = models.ForeignKey("accounts.Account", blank=False, null=False)
    venue_account = models.ForeignKey("accounts.VenueAccount", blank=False, null=False)