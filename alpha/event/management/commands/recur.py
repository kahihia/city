#command to search for recurring events and adjust their dates accordingly
from django.core.management.base import BaseCommand,CommandError
from event.models import Event
import datetime
from datetime import date, timedelta

class Command(BaseCommand):
    args = 'test'
    help = 'Runs to set respective dates for recurring events'
    
    def handle(self, *args, **options):
        subjects = Event.events.filter(frequency=1)
        for i in subjects:
            print i
            time = i.start_time
            d = time+timedelta(days=1)
            i.start_time=d
            i.save()
            print d
        
         
