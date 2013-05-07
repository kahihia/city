from event.models import Event
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from twilio.rest import TwilioRestClient
from django.conf import settings


def remind_account_about_events(account, events):
    if account.reminder_with_email:
        remind_account_about_events_with_email(account, events)

    if account.reminder_with_sms:
        remind_account_about_events_with_sms(account, events)


def find_similar_events(events):
    basic_event_ids = ",".join([str(id) for id in list(set(events.values_list('id', flat=True)))])
     # TODO: create similarity matrix for best performance(if we will need this)
    similar_events = Event.events.raw("""
        SELECT event_event.*, array_agg(tag_id) as tags,
            smlar(
                (
                    SELECT array_agg(tag_id) as event_tags
                    FROM event_event, taggit_taggeditem
                    WHERE event_event.id=taggit_taggeditem.object_id
                    AND event_event.id IN (%s)
                ),
                array_agg(tag_id)
            ) as similiarity
        FROM event_event left join event_singleevent
        ON event_event.id=event_singleevent.event_id inner join taggit_taggeditem
        ON event_event.id=taggit_taggeditem.object_id
        WHERE event_singleevent.start_time >= now()
        AND event_event.id NOT IN (%s)
        GROUP BY taggit_taggeditem.object_id, event_event.id
        ORDER BY similiarity DESC
        LIMIT 10
    """ % (basic_event_ids, basic_event_ids))

    return similar_events


def remind_account_about_events_with_email(account, events):
    featured_events = Event.featured_events.all()[:4]  # .exclude(id__in=events.values_list('id', flat=True))[:4]

    similar_events = find_similar_events(events)

    subject = "Upcoming events from cityfusion"

    message = render_to_string('accounts/emails/reminder_email.html', {
            "featured_events": featured_events,
            "events": events,
            "similar_events": similar_events,
            "STATIC_URL": "/static/",
            "site": "http://%s" % Site.objects.get_current().domain
        })

    msg = EmailMessage(subject,
               message,
               "reminder@cityfusion.ca",
               [account.user.email])
    msg.content_subtype = 'html'
    msg.send()

    return message


def remind_account_about_events_with_sms(account, events):
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    for event in events:

        body = render_to_string('accounts/sms/reminder_sms.txt', {
            "event": event
        })

        client.sms.messages.create(
            to=account.reminder_phonenumber,
            from_=settings.TWILIO_NUMBER,
            body=body
        )


def inform_account_about_events_with_tag(account, events, tags_in_venues):
    if account.reminder_with_email:
        inform_account_about_events_with_tag_with_email(account, events, tags_in_venues)

    if account.reminder_with_sms:
        inform_account_about_events_with_tag_with_sms(account, events, tags_in_venues)


def inform_account_about_events_with_tag_with_email(account, events, tags_in_venues):
    featured_events = Event.featured_events.all()[:4]  # .exclude(id__in=events.values_list('id', flat=True))[:4]

    similar_events = find_similar_events(events)

    subject = "New Events in cityfusion"

    message = render_to_string('accounts/emails/in_the_loop_email.html', {
            "featured_events": featured_events,
            "events": events,
            "similar_events": similar_events,
            "STATIC_URL": "/static/",
            "site": "http://%s" % Site.objects.get_current().domain,
            "tags_in_venues": tags_in_venues
        })

    msg = EmailMessage(subject,
        message,
        "reminder@cityfusion.ca",
        [account.user.email])

    msg.content_subtype = 'html'

    msg.send()

    return message


def inform_account_about_events_with_tag_with_sms(account, events, tags_in_venues):
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    account_tags = account.in_the_loop_tags.values_list('name', flat=True)

    for event in events:
        event_tags = event.tags.values_list('name', flat=True)
        tags_intersection = list(set(account_tags) & set(event_tags))

        body = render_to_string('accounts/sms/in_the_loop_sms.txt', {
            "event": event,
            "tags": tags_intersection
        })

        client.sms.messages.create(
            to=account.reminder_phonenumber,
            from_=settings.TWILIO_NUMBER,
            body=body
        )
