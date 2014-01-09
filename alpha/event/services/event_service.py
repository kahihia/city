import json
import datetime

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import transaction
from django.contrib.auth.models import User

from moneyed import Money, CAD

from event.settings import DEFAULT_FROM_EMAIL
from event.services import venue_service, event_occurrence_service
from event.models import Event, EventAttachment, EventImage, EventTransferring
from notices.models import Notice
from notices import services as notice_service


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

    if user.is_authenticated():
        event.owner = user
        event.email = user.email

    event = event.save()

    event_occurrence_service.update_occurrences(data, event)    

    event.eventattachment_set.all().delete()
    if data["attachments"]:
        attachments = data["attachments"].split(";")
        for attachment in attachments:
            EventAttachment.objects.get_or_create(
                event=event,
                attachment=attachment.replace(settings.MEDIA_URL, "")
            )

    event.eventimage_set.all().delete()
    if data["images"]:
        images = json.loads(data["images"])["images"]

        for image in images:
            image_src, cropping, order = image["filepath"], image["cropping"], image["order"]
            EventImage.objects.get_or_create(
                event=event,
                picture=image_src.replace(settings.MEDIA_URL, ""),
                cropping=cropping,
                order=order
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


def prepare_initial_attachments(event):
    attachments = event.eventattachment_set.values_list("attachment", flat=True)
    attachments = map(lambda attachment: "/media/%s" % attachment, attachments)
    return ";".join(attachments)


def prepare_initial_images(event):
    images = event.eventimage_set.order_by("order")

    images_json = {
        "images": map(lambda imageModel: {
                "filepath": "/media/%s" % imageModel.picture,
                "cropping": imageModel.cropping
            }, images)
    }
    
    return json.dumps(images_json)


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
        "attachments": prepare_initial_attachments(event),
        "images": prepare_initial_images(event),
        "tags": event.tags_representation,
        "description_json": json.dumps(description_json)
    }


def remove_event(authentication_key):
    """ Remove event with the given identifier.

    @type authentication_key: unicode
    @rtype: bool
    """
    try:
        event = Event.events.get(authentication_key__exact=authentication_key)
        date_now = datetime.datetime.now()
        featured_events = list(event.featuredevent_set.filter(end_time__gte=date_now).all())

        if featured_events:
            bonus = Money(0, CAD)
            for featured_event in featured_events:
                if featured_event.start_time < date_now:
                    bonus += (featured_event.end_time - date_now).days * Money(2, CAD)
                else:
                    bonus += (featured_event.end_time - featured_event.start_time).days * Money(2, CAD)

            account = event.owner.get_profile()
            account.bonus_budget += bonus
            account.save(update_fields=['bonus_budget'])

        event.delete()
        return True
    except Event.DoesNotExist:
        return False


def change_event_owner(event_id, owner_id, identifier, is_last, session):
    """ Change owner of the event with the given id.

    @type event_id: int
    @type owner_id: int
    @param owner_id: new event's owner id
    @type identifier: unicode
    @param identifier: current transferring process identifier
    @type is_last: bool
    @param is_last: if the event is last in the transfer queue
    @type session: django.contrib.sessions.backends.db.SessionStore
    @rtype: bool
    """
    success = False
    try:
        if event_id and owner_id and identifier:
            event = Event.events.get(pk=event_id)
            owner = User.objects.get(id=owner_id)
            stored_identifier = session.get('transfer_identifier', '')

            if not stored_identifier or identifier != stored_identifier:
                event_transferring = EventTransferring.objects.create(target=owner)
                session['transfer_identifier'] = identifier
                session['transfer_id'] = event_transferring.id
            else:
                event_transferring = EventTransferring.objects.get(pk=int(session['transfer_id']))

            event_transferring.events.add(event)
            success = True
    except Exception:
        success = False
    finally:
        if is_last and owner and event_transferring:
            events = list(event_transferring.events.all())
            event_links = []
            for event_item in events:
                date = event_item.next_day().start_time.strftime('%Y-%m-%d')
                link = reverse('event_view', kwargs={'slug': event_item.slug, 'date': date})
                event_links.append((event_item.name, link))

            target_name = owner.username
            target_link = reverse('userena_profile_detail', kwargs={'username': owner.username})
            notice_service.create_notice(notice_type='transferring_to_owner',
                                     user=event.owner,
                                     notice_data={
                                         'event_count': len(events),
                                         'event_links': event_links,
                                         'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
                                         'target_name': target_name,
                                         'target_link': target_link,
                                     })

            notice_service.create_notice('transferring', owner, {
                'subject': 'CityFusion: events have been transferred to you.',
                'user': owner,
                'events': events
            }, {
                'event_count': len(events),
                'event_links': event_links,
                'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
                'accept_link': reverse('accept_transferring', kwargs={'transferring_id': event_transferring.id}),
                'reject_link': reverse('reject_transferring', kwargs={'transferring_id': event_transferring.id})
            })
    return success


def accept_events_transferring(transferring_id, notice_id):
    """ Accept events transferring.

    @type transferring_id: int
    @type notice_id: int
    @rtype: bool
    """
    result = False
    try:
        transferring = EventTransferring.objects.get(pk=transferring_id)
    except EventTransferring.DoesNotExist:
        transferring = None

    if transferring and transferring.target:
        event_list = list(transferring.events.all())
        from_user = event_list[0].owner if len(event_list) else None
        target = transferring.target

        for event in event_list:
            event.owner = transferring.target
            event.save()

            transferring.events.remove(event)

        transferring.delete()

        try:
            notice = Notice.objects.get(pk=notice_id)
        except Notice.DoesNotExist:
            notice = None

        if notice:
            notice_data = json.loads(notice.log)
            notice_data['state'] = 'Accepted'
            notice.log = json.dumps(notice_data)
            notice.read = True
            notice.save()

        event_links = []
        for event_item in event_list:
            date = event_item.next_day().start_time.strftime('%Y-%m-%d')
            link = reverse('event_view', kwargs={'slug': event_item.slug, 'date': date})
            event_links.append((event_item.name, link))

        target_name = target.username
        target_link = reverse('userena_profile_detail', kwargs={'username': target.username})
        notice_service.create_notice('transferring_accepting', from_user, {
            'subject': 'Cityfusion: transferring of your events has been accepted.',
            'user': from_user,
            'events': event_list,
            'target_name': target_name,
            'target_link': target_link,
        }, {
            'event_count': len(event_list),
            'event_links': event_links,
            'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
            'target_name': target_name,
            'target_link': target_link,
        })

        result = True
    return result


def reject_events_transferring(transferring_id, notice_id):
    """ Reject events transferring.

    @type transferring_id: int
    @type notice_id: int
    @rtype: bool
    """
    result = False
    try:
        transferring = EventTransferring.objects.get(pk=transferring_id)
    except EventTransferring.DoesNotExist:
        transferring = None

    if transferring and transferring.target:
        event_list = list(transferring.events.all())
        from_user = event_list[0].owner if len(event_list) else None
        target = transferring.target

        for event in transferring.events.all():
            transferring.events.remove(event)

        transferring.delete()
        try:
            notice = Notice.objects.get(pk=notice_id)
        except Notice.DoesNotExist:
            notice = None

        if notice:
            notice_data = json.loads(notice.log)
            notice_data['state'] = 'Rejected'
            notice.log = json.dumps(notice_data)
            notice.read = True
            notice.save()

        event_links = []
        for event_item in event_list:
            date = event_item.next_day().start_time.strftime('%Y-%m-%d')
            link = reverse('event_view', kwargs={'slug': event_item.slug, 'date': date})
            event_links.append((event_item.name, link))

        target_name = target.username
        target_link = reverse('userena_profile_detail', kwargs={'username': target.username})
        notice_service.create_notice('transferring_rejecting', from_user, {
            'subject': 'Cityfusion: transferring of your events has been rejected.',
            'user': from_user,
            'events': event_list,
            'target_name': target_name,
            'target_link': target_link,
        }, {
            'event_count': len(event_list),
            'event_links': event_links,
            'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
            'target_name': target_name,
            'target_link': target_link,
        })

        result = True
    return result