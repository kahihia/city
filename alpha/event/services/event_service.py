import json

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from django.core.mail.message import EmailMessage
from django.conf import settings

from event.settings import DEFAULT_FROM_EMAIL
from event.services import venue_service, event_occurrence_service
from event.models import EventAttachment

from django.contrib.sites.models import Site

from django.db import transaction


def send_event_details_email(event):
    current_site = Site.objects.get_current().domain
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


@transaction.commit_on_success
def save_event(user, data, form):
    event = form.save()

    event.venue = venue_service.get_venue_from_request_data(event, data)

    event_occurrence_service.update_occurrences(data, event)

    if user.is_authenticated():
        event.owner = user
        event.email = user.email

    if data["picture_src"]:
        event.picture.name = data["picture_src"].replace(settings.MEDIA_URL, "")

    event = event.save()
    event.eventattachment_set.all().delete()

    if data["attachments"]:
        attachments = data["attachments"].split(";")
        for attachment in attachments:
            EventAttachment.objects.get_or_create(
                event=event,
                attachment=attachment.replace(settings.MEDIA_URL, "")
            )

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


def prepare_initial_attachments(event):
    attachments = event.eventattachment_set.values_list("attachment", flat=True)
    attachments = map(lambda attachment: "/media/%s" % attachment, attachments)
    return ";".join(attachments)


def prepare_initial_images(event):
    images = event.eventimage_set.all()
    images = [
        "/media/%s!%s" % (imageModel.picture, imageModel.cropping) for imageModel in images
    ]

    return ";".join(images)


def prepare_initial_venue_id(event):
    if event.venue:
        return event.venue.id
    return None


def prepare_initial_event_data_for_edit(event):
    when_json, description_json = event_occurrence_service.prepare_initial_when_and_description(event)
    occurrences = event_occurrence_service.prepare_initial_occurrences(event)

    return {
        "linking_venue_mode": "EXIST",
        "venue_identifier": prepare_initial_venue_id(event),
        "place": prepare_initial_place(event),            
        "location": prepare_initial_location(event),
        "picture_src": prepare_initial_picture_src(event),
        "attachments": prepare_initial_attachments(event),
        "images": prepare_initial_images(event),
        "when_json": json.dumps(when_json),
        "description_json": json.dumps(description_json),
        "occurrences_json": json.dumps(occurrences)
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
        "attachments": prepare_initial_attachments(event),
        "images": prepare_initial_images(event),
        "tags": event.tags_representation,
        "description_json": json.dumps(description_json)
    }
