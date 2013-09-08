import re
from datetime import datetime, timedelta

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail.message import EmailMessage
from django.core.serializers import serialize
from django.contrib.gis.db import models

from accounts.models import Account, AccountReminding
from .models import Event, SingleEvent, AuditEvent, AuditPhrase, phrases_query
from .settings import DEFAULT_FROM_EMAIL, DELETED_EVENTS_REMINDING_INTERVAL
from django.contrib.sites.models import Site


def audit_event_catch(instance=None, created=False, **kwargs):
    if instance.audited:
        return
    bad_phrases = phrases_query()
    name_search_result = re.findall(bad_phrases, instance.name, re.I)
    description_search_result = re.findall(bad_phrases, instance.description, re.I)
    if name_search_result or description_search_result:
        audit_event = AuditEvent(
            event_ptr_id=instance.pk
        )
        audit_event.__dict__.update(instance.__dict__)
        audit_event.save()
        phrases = AuditPhrase.objects.filter(
            phrase__in=(name_search_result + description_search_result)
        )
        for phrase in phrases:
            audit_event.phrases.add(phrase)

        current_site = Site.objects.get_current().domain

        subject = 'Bad phrases have been caught!'

        message = render_to_string('audit/bad_phrases_email.txt', {
            'site': current_site,
            'event': audit_event,
            'phrases': phrases
        })

        msg = EmailMessage(subject,
                message,
                DEFAULT_FROM_EMAIL,
                map(lambda x: x[1], settings.ADMINS))

        msg.content_subtype = 'html'


def after_single_event_delete(instance=None, **kwargs):
    existing_reminders = Account.reminder_single_events.through.objects.filter(singleevent_id=instance.id)
    archived_data = serialize('json', [instance], relations={'event': {'relations': ('venue',)}})
    notification_time = datetime.now() + timedelta(minutes=int(DELETED_EVENTS_REMINDING_INTERVAL) + 1)
    for existing_reminder in existing_reminders:
        reminder = AccountReminding(
            account=existing_reminder.account,
            notification_time=notification_time,
            notification_type='DELETED_EVENT',
            archived_data=archived_data
        )

        reminder.save()

    Account.reminder_single_events.through.objects.filter(singleevent_id=instance.id).delete()


models.signals.post_save.connect(audit_event_catch, sender=Event)
models.signals.pre_delete.connect(after_single_event_delete, sender=SingleEvent)

# def audit_single_event(instance=None, created=False, **kwargs):
#     bad_phrases = phrases_query()
#     description_search_result = re.findall(bad_phrases, instance.description)
#     if description_search_result:
#         audit_event = AuditSingleEvent(
#             event=instance,
#             phrases=AuditPhrase.objects.filter(
#                 name__in=description_search_result
#             )
#         )
#     audit_event.save()
# models.signals.post_save.connect(audit_single_event, sender=SingleEvent)