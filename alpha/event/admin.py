from django.contrib import admin
from alpha.event.models import Event, SingleEvent
from alpha.event.models import Venue
from alpha.event.models import Reminder
admin.site.register(Event)
admin.site.register(SingleEvent)
admin.site.register(Venue)
admin.site.register(Reminder)
