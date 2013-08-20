import datetime
import time
import json

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from django.core.mail.message import EmailMessage
from django.conf import settings

import dateutil.parser as dateparser

from event.settings import DEFAULT_FROM_EMAIL
from event.services import venue_service

from event.models import SingleEvent


def send_event_details_email(event):
    current_site = settings.EVENT_EMAIL_SITE
    subject = render_to_string('events/create/creation_email_subject.txt', {
            'site': current_site,
            'title': mark_safe(event.name)
        })

    subject = ''.join(subject.splitlines())  # Email subjects are all on one line

    message = render_to_string('events/create/creation_email.txt', {
            'authentication_key': event.authentication_key,
            'slug': event.slug,
            'site': current_site
        })

    msg = EmailMessage(subject,
               message,
               DEFAULT_FROM_EMAIL,
               [event.email])
    msg.content_subtype = 'html'
    msg.send()    


def save_when_and_description(data, event):
    when_json = json.loads(data["when_json"])
    description_json = json.loads(data["description_json"])

    event.description = description_json['default']
    single_events = list(event.single_events.all())  # existing single events of the current event
    single_events_to_save_ids = []

    for year, months in when_json.iteritems():
        for month, days in months.iteritems():
            for day, times in days.iteritems():
                date = datetime.datetime(int(year), int(month), int(day), 0, 0)
                if date.strftime("%m/%d/%Y") in description_json['days']:
                    description = description_json['days'][date.strftime("%m/%d/%Y")]
                else:
                    description = ""
                start_time = time.strptime(times["start"], '%I:%M %p')
                start = datetime.datetime(int(year), int(month), int(day), start_time[3], start_time[4])

                end_time = time.strptime(times["end"], '%I:%M %p')
                end = datetime.datetime(int(year), int(month), int(day), end_time[3], end_time[4])

                single_event = SingleEvent(
                    event=event,
                    start_time=start.strftime('%Y-%m-%d %H:%M'),
                    end_time=end.strftime('%Y-%m-%d %H:%M'),
                    description=description
                )

                ext_single_event = get_identic_single_event_from_list(single_event, single_events)
                if not ext_single_event:
                    single_event.save()
                else:
                    single_events_to_save_ids.append(ext_single_event.id)

    single_events_to_delete_ids = list(set([item.id for item in single_events]).difference(single_events_to_save_ids))
    SingleEvent.objects.filter(id__in=single_events_to_delete_ids).delete()


def save_event(user, data, form):
    event = form.save()

    event.venue = venue_service.get_venue_from_request_data(event, data)

    save_when_and_description(data, event)

    if user.is_authenticated():
        event.owner = user
        event.email = user.email

    if data["picture_src"]:
        event.picture.name = data["picture_src"].replace(settings.MEDIA_URL, "")

    event = event.save()

    return event


def prepare_initial_place(event):
    venue = event.venue

    full_parts = [x for x in [venue.name, venue.street, venue.city.name, venue.country.name] if x]
    place = {
        "full": ", ".join(full_parts),
        "venue": venue.name,
        "street": venue.street,
        "city": venue.city.name,
        "country": venue.country.name,
        "longtitude": venue.location.x,
        "latitude": venue.location.y
    }

    return place


def prepare_initial_location(event):
    return (event.venue.location.x, event.venue.location.y)


def prepare_initial_picture_src(event):
    return "/media/%s" % event.picture


def prepare_initial_venue_id(event):
    if event.venue:
        return event.venue.id
    return None


def prepare_initial_event_data_for_edit(event):
    when_json = {}
    description_json = {
        "default": event.description,
        "days": {}
    }

    single_events = SingleEvent.objects.filter(event=event)

    for single_event in single_events:
        start_time = single_event.start_time
        year = start_time.year
        month = start_time.month
        day = start_time.day

        if not year in when_json:
            when_json[year] = {}

        if not month in when_json[year]:
            when_json[year][month] = {}

        when_json[year][month][day] = {
            "start": start_time.strftime('%I:%M %p'),
            "end": single_event.end_time.strftime('%I:%M %p')
        }

        description_json["days"][start_time.strftime("%m/%d/%Y")] = single_event.description

    return {
        "linking_venue_mode": "EXIST",
        "venue_identifier": prepare_initial_venue_id(event),
        "place": prepare_initial_place(event),            
        "location": prepare_initial_location(event),
        "picture_src": prepare_initial_picture_src(event),
        "when_json": json.dumps(when_json),
        "description_json": json.dumps(description_json)
    }


def prepare_initial_event_data_for_copy(event):
    description_json = {
        "default": event.description,
        "days": {}
    }
    return {
        "linking_venue_mode": "EXIST",
        "venue_identifier": prepare_initial_venue_id(event),
        "place": prepare_initial_place(event),
        "location": prepare_initial_location(event),
        "picture_src": prepare_initial_picture_src(event),
        "tags": event.tags_representation,
        "description_json": json.dumps(description_json)
    }


def get_identic_single_event_from_list(single_event, single_event_list):
    for item in single_event_list:
        if item.start_time == dateparser.parse(single_event.start_time) \
            and item.end_time == dateparser.parse(single_event.end_time) \
                and item.description == single_event.description:
            return item

    return False