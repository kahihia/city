from datetime import datetime
from event.models import Event
from accounts.models import InTheLoopSchedule
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string


def remind_account_about_events(account, events):
    basic_event_ids = ",".join([str(id) for id in list(set(events.values_list('id', flat=True)))])

    featured_events = Event.featured_events.all()[:4]  # .exclude(id__in=events.values_list('id', flat=True))[:4]

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


def inform_account_about_events_with_tag(account, events, tags_in_venues):
    basic_event_ids = ",".join([str(id) for id in list(set(events.values_list('id', flat=True)))])

    featured_events = Event.featured_events.all()[:4]  # .exclude(id__in=events.values_list('id', flat=True))[:4]

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
