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
    reminder_events = models.ManyToManyField("event.Event", blank=True, null=True)

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
        return Event.future_events.filter(tagged_items__tag__name__in=self.in_the_loop_tags.all().values("name"))

    def reminder_events_in_future(self):
        return Event.future_events.filter(id__in=self.reminder_events.values("id"))


#Make sure we create a Account when creating a User
def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


def add_events_to_schedule(account, events):
    for event in events:
        event_days = SingleEvent.future_days.filter(event_id=event.id)
        for event_day in event_days:
            if account.reminder_days_before_event:
                notification_time = event_day.start_time - timedelta(days=int(account.reminder_days_before_event))
                if notification_time > datetime.datetime.now():
                    reminding = AccountReminding(
                        account=account,
                        event=event,
                        notification_time=notification_time,
                        notification_type='DAYS_BEFORE_EVENT'
                    )
                    reminding.save()
            if account.reminder_hours_before_event:
                notification_time = event_day.start_time - timedelta(hours=int(account.reminder_hours_before_event))
                if notification_time > datetime.datetime.now():
                    reminding = AccountReminding(
                        account=account,
                        event=event,
                        notification_time=notification_time,
                        notification_type='HOURS_BEFORE_EVENT'
                    )
                    reminding.save()


def sync_schedule_after_reminder_events_was_modified(sender, **kwargs):
    if kwargs['action'] == 'post_add':
        events = Event.future_events.filter(id__in=kwargs["pk_set"])

        add_events_to_schedule(kwargs['instance'], events)

    if kwargs['action'] == 'post_remove':
        AccountReminding.hots.filter(event__id__in=kwargs["pk_set"]).delete()


def sync_schedule_after_reminder_settings_was_changed(sender, instance, created, **kwargs):
    AccountReminding.objects.filter(account_id=instance.id).delete()
    add_events_to_schedule(instance, instance.reminder_events.all())


post_save.connect(create_facebook_profile, sender=User)
post_save.connect(sync_schedule_after_reminder_settings_was_changed, sender=Account)

m2m_changed.connect(sync_schedule_after_reminder_events_was_modified, sender=Account.reminder_events.through)


class RemindingManager(models.Manager):
    def get_query_set(self):
        return super(RemindingManager, self).get_query_set().filter(notification_time__lte=datetime.datetime.now(), done=False)


NOTIFICATION_TYPES = (
    ('DAYS_BEFORE_EVENT', 'Days before event'),
    ('HOURS_BEFORE_EVENT', 'Hours before event'),
    ('ON_WEEK_DAY', 'On week day'),
)


class AccountReminding(models.Model):
    account = models.ForeignKey(Account)
    event = models.ForeignKey('event.Event')
    notification_time = models.DateTimeField('notification time', auto_now=False, auto_now_add=False)
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES)
    done = models.BooleanField(default=False)

    objects = models.Manager()
    hots = RemindingManager()

    def processed(self):
        self.done = True
        self.save()

    def __unicode__(self):
        status = "QUEUE"
        if self.done:
            status = "DONE"
        return "%s at (%s) - %s" % (self.event.name, self.notification_time, status)


class NewInTheLoopEventManager(models.Manager):
    def get_query_set(self):
        return super(NewInTheLoopEventManager, self).get_query_set().filter(processed=False)


class InTheLoopSchedule(models.Model):
    event = models.ForeignKey('event.Event')
    processed = models.BooleanField(default=False)

    objects = models.Manager()
    new_events = NewInTheLoopEventManager()

    def process(self):
        self.processed = True
        self.save()

    @staticmethod
    def unprocessed_for_account(account):
        tags = account.in_the_loop_tags.values_list("name", flat=True)
        event_ids = InTheLoopSchedule.new_events.filter(event__tagged_items__tag__name__in=tags).values_list("event_id", flat=True)
        return Event.future_events.filter(id__in=event_ids)

    def __unicode__(self):
        status = "QUEUE"
        if self.processed:
            status = "PROCESSED"
        return "%s - %s" % (self.event.name, status)


def add_to_in_the_loop_schedule(sender, instance, created, **kwargs):
    InTheLoopSchedule.objects.filter(event_id=instance.id).delete()
    InTheLoopSchedule(event=instance).save()


models.signals.post_save.connect(add_to_in_the_loop_schedule, sender=Event)
