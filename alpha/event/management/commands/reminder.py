from django.core.management.base import BaseCommand,CommandError
from event.models import Reminder
import datetime
import smtplib
from django.template.loader import render_to_string


FROMADDR = "cityfusion12@gmail.com"
LOGIN    = FROMADDR
PASSWORD = "fusion12"

#class Command(BaseCommand):
    args = 'test'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        today = datetime.datetime.now()
        comp = datetime.datetime(today.year, today.month, today.day)
        
        shows = Reminder.objects.all()
        for i in shows:
            print i
            day = i.date
            comp2 = datetime.datetime(day.year, day.month, day.day)
            if comp2 == comp:
                print i
        
                subject = "Event Remider"
                msgg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
                     % (FROMADDR, (i.email), subject) )
                message = "The event %s is set to take place today...do not miss out" % i.event
                msgg += message
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.set_debuglevel(1)
                server.ehlo() 
                server.starttls()
                server.login(LOGIN, PASSWORD)
                server.sendmail(FROMADDR, i.email, msgg)
                server.quit()
                gh = open("foo.txt", "a")
       	        gh.write("new line\n")
