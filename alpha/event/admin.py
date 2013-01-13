from django.contrib import admin
from event.models import Event, SingleEvent
from event.models import Venue
from event.models import Reminder
admin.site.register(Event)
admin.site.register(SingleEvent)
admin.site.register(Venue)
admin.site.register(Reminder)
