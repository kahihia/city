import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from django.contrib.gis.db import models
from taggit_autosuggest.managers import TaggableManager

from event.models import Event, SingleEvent

from phonenumber_field.modelfields import PhoneNumberField

from django_facebook.models import FacebookProfileModel

from django.db.models.signals import post_save, m2m_changed

DAYS_OF_WEEK = (
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
)


class Account(UserenaBaseProfile, FacebookProfileModel):
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='my_profile')
    # here will be location, site, reminder settings, loop tags, order

    location = models.PointField(blank=True, null=True)
    venue = models.ForeignKey('event.Venue', blank=True, null=True)

    website = models.URLField(blank=True, null=True, default='')

    # Reminder

    # remind options
    # remind time before event
    reminder_time_before_event = models.TimeField(blank=True, null=True)
    reminder_days_before_event = models.IntegerField(blank=True, null=True)
    reminder_hours_before_event = models.IntegerField(blank=True, null=True)

    # remind on week day
    reminder_on_week_day = models.CharField(max_length=1, choices=DAYS_OF_WEEK, blank=True, null=True, default=0)
    reminder_on_week_day_at_time = models.TimeField(blank=True, null=True)

    # remind types

    reminder_with_website = models.BooleanField(default=True)
    reminder_with_email = models.BooleanField(default=True)
    reminder_with_sms = models.BooleanField(default=False)

    reminder_email = models.EmailField(blank=True, null=True)
    reminder_phonenumber = PhoneNumberField(blank=True, null=True)

    # events for remind
    reminder_events = models.ManyToManyField("event.SingleEvent", blank=True, null=True)

    in_the_loop_tags = TaggableManager(blank=True)

    # In the Loop

    # in the loop options
    # in the loop time before event
    in_the_loop_days_before_event = models.IntegerField(blank=True, null=True)
    in_the_loop_hours_before_event = models.IntegerField(blank=True, null=True)

    # in the loop on week day
    in_the_loop_on_week_day = models.CharField(max_length=1, choices=DAYS_OF_WEEK, blank=True, null=True, default=0)
    in_the_loop_on_week_day_at_time = models.TimeField(blank=True, null=True)

    # in the loop types

    in_the_loop_with_website = models.BooleanField(default=True)
    in_the_loop_with_email = models.BooleanField(default=True)
    in_the_loop_with_sms = models.BooleanField(default=False)

    in_the_loop_email = models.EmailField(blank=True, null=True)
    in_the_loop_phonenumber = PhoneNumberField(blank=True, null=True)

    def in_the_loop_events(self):
        return SingleEvent.objects.filter(event__tagged_items__tag__name__in=self.in_the_loop_tags.all().values("name"))


#Make sure we create a Account when creating a User
def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


def add_event_days_to_schedule(account, event_days):
    for event_day in event_days:
        if account.reminder_days_before_event:
            notification_time = event_day.start_time - timedelta(days=int(account.reminder_days_before_event))
            reminding = AccountReminding(
                account=account,
                event_day=event_day,
                notification_time=notification_time,
                notification_type='DAYS_BEFORE_EVENT'
            )
            reminding.save()
        if account.reminder_hours_before_event:
            notification_time = event_day.start_time - timedelta(hours=int(account.reminder_hours_before_event))
            reminding = AccountReminding(
                account=account,
                event_day=event_day,
                notification_time=notification_time,
                notification_type='HOURS_BEFORE_EVENT'
            )
            reminding.save()


def sync_schedule_after_reminder_events_was_modified(sender, **kwargs):
    if kwargs['action'] == 'post_add':
        event_days = SingleEvent.objects.filter(id__in=kwargs["pk_set"])

        add_event_days_to_schedule(kwargs['instance'], event_days)

    if kwargs['action'] == 'post_remove':
        AccountReminding.hots.filter(event_day__id__in=kwargs["pk_set"]).delete()


def sync_schedule_after_reminder_settings_was_changed(sender, instance, created, **kwargs):
    AccountReminding.hots.filter(account_id=instance.id).delete()
    add_event_days_to_schedule(instance, instance.reminder_events)


post_save.connect(create_facebook_profile, sender=User)
post_save.connect(sync_schedule_after_reminder_settings_was_changed, sender=Account)

m2m_changed.connect(sync_schedule_after_reminder_events_was_modified, sender=Account.reminder_events.through)


class RemindingManager(models.Manager):
    def get_query_set(self):
        return super(RemindingManager, self).get_query_set().filter(notification_time__gte=datetime.datetime.now(), done=False)


NOTIFICATION_TYPES = (
    ('DAYS_BEFORE_EVENT', 'Days before event'),
    ('HOURS_BEFORE_EVENT', 'Hours before event'),
    ('ON_WEEK_DAY', 'On week day'),
)


class AccountReminding(models.Model):
    account = models.ForeignKey(Account)
    event_day = models.ForeignKey('event.SingleEvent')
    notification_time = models.DateTimeField('notification time', auto_now=False, auto_now_add=False)
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES)
    done = models.BooleanField(default=False)

    hots = RemindingManager()

    objects = models.Manager()

    def processed(self):
        self.done = True
        self.save()
