from django.contrib import admin
from alpha.event.models import Event
from alpha.event.models import CanadianVenue
from alpha.event.models import Recurrence
admin.site.register(Recurrence)
admin.site.register(Event)
admin.site.register(CanadianVenue)
