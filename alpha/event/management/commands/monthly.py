#command to search for recurring events and adjust their dates accordingly
from django.core.management.base import BaseCommand,CommandError
from event.models import Event
import datetime
from datetime import date, timedelta

class Command(BaseCommand):
    args = 'test'
    help = 'Runs to set respective dates for recurring events'
    
    def handle(self, *args, **options):
        subject = Event.events.filter(frequency=30)
        for u in subject:
            print u
            time = u.start_time
            f = time+timedelta(days=30)
            i.start_time=f
            i.save()
            print f
