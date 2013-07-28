from django.contrib.gis.db import models

class ActiveManager(models.Manager):
    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(processed=False)


class ReportEvent(models.Model):
    event = models.ForeignKey("event.Event")
    account = models.ForeignKey("accounts.Account", blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    processed  = models.BooleanField(default=False)

    active = ActiveManager()


class ClaimEvent(models.Model):
    event = models.ForeignKey("event.Event")
    account = models.ForeignKey("accounts.Account")
    message = models.TextField(blank=True, null=True)
    processed  = models.BooleanField(default=False)

    active = ActiveManager()


CF_ADMIN_MENU = {
    "report_event": {
        "urlname": "report_event_list",
        "linktext": "Reports"
    },
    "claim_event": {
        "urlname": "claim_event_list",
        "linktext": "Claims"
    }
}