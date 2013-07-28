import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from django.contrib.gis.db import models
from taggit_autosuggest.managers import TaggableManager

from event.models import Event, SingleEvent, Venue

from django_facebook.models import FacebookProfileModel

from django.db.models.signals import post_save, m2m_changed

from image_cropping import ImageCropField, ImageRatioField

from django.template.defaultfilters import slugify

from django.core.exceptions import ObjectDoesNotExist

from advertising.models import Advertising
from cities.models import Region, City
from django.db.models import Q


REMINDER_TYPES = (
    ("HOURS", "Hours before event"),
    ("DAYS", "Days before event"),
    ("WEEKDAY", "On week day")
)


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

    native_region = models.ForeignKey(Region, blank=True, null=True, related_name="native_for_accounts")
    not_from_canada = models.BooleanField(default=False)

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

    reminder_active_type = models.CharField(max_length=10, choices=REMINDER_TYPES, default="HOURS")

    # remind types

    reminder_with_website = models.BooleanField(default=True)
    reminder_with_email = models.BooleanField(default=True)
    reminder_with_sms = models.BooleanField(default=False)

    reminder_email = models.EmailField(blank=True, null=True)
    reminder_phonenumber = models.CharField(max_length=15, blank=True, null=True)

    # events for remind
    reminder_events = models.ManyToManyField("event.Event", blank=True, null=True)

    in_the_loop_tags = TaggableManager(blank=True)

    # In the Loop

    in_the_loop_with_website = models.BooleanField(default=True)
    in_the_loop_with_email = models.BooleanField(default=True)
    in_the_loop_with_sms = models.BooleanField(default=False)

    in_the_loop_email = models.EmailField(blank=True, null=True)
    in_the_loop_phonenumber = models.CharField(max_length=15, blank=True, null=True)

    all_of_canada = models.BooleanField()
    regions = models.ManyToManyField(Region)
    cities = models.ManyToManyField(City)

    def future_events(self):
        return Event.future_events.filter(owner_id=self.user.id)

    def in_the_loop_events(self):
        return Event.future_events.filter(tagged_items__tag__name__in=self.in_the_loop_tags.all().values("name"))

    def reminder_events_in_future(self):
        return Event.future_events.filter(id__in=self.reminder_events.values("id"))

    def ads(self):
        return Advertising.objects.filter(campaign__account__id=self.id)

    def taxes(self):
        if self.native_region:
            return AccountTax.objects.filter(regions__id=self.native_region.id)
        else:
            return []

    def reminder_weekday(self):
        if self.reminder_active_type=="WEEKDAY":
            return DAYS_OF_WEEK
        else:
            return "%s" % self.reminder_on_week_day


    def in_the_loop_tag_names(self):
        return self.in_the_loop_tags.all().values_list("name", flat=True)


def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


def add_events_to_schedule(account, events):
    if account.reminder_active_type in ["DAYS", "HOURS"]:
        for event in events:
            event_days = SingleEvent.future_events.filter(event_id=event.id)

            for event_day in event_days:
                if account.reminder_active_type == "DAYS":
                    notification_time = event_day.start_time - timedelta(days=int(account.reminder_days_before_event))
                if account.reminder_active_type == "HOURS":
                    notification_time = event_day.start_time - timedelta(hours=int(account.reminder_hours_before_event))

                if notification_time > datetime.datetime.now():
                    reminding = AccountReminding(
                        account=account,
                        event=event,
                        notification_time=notification_time,
                        notification_type=("%s_BEFORE_EVENT" % account.reminder_active_type)
                    )
                    reminding.save()


def sync_schedule_after_reminder_events_was_modified(sender, **kwargs):
    if kwargs['action'] == 'post_add':
        events = Event.future_events.filter(id__in=kwargs["pk_set"])

        add_events_to_schedule(kwargs['instance'], events)

    if kwargs['action'] == 'post_remove':
        AccountReminding.objects.filter(event__id__in=kwargs["pk_set"]).delete()


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
        region_ids = account.regions.all().values_list("id", flat=True)
        city_ids = account.cities.all().values_list("id", flat=True)

        if account.all_of_canada:
            location_query = Q(venue__country__name="Canada")
        else:
            location_query = Q(venue__city__id__in=city_ids) | Q(venue__city__region__id__in=region_ids) | Q(venue__city__subregion__id__in=region_ids)

        event_ids = InTheLoopSchedule.new_events.filter(
            event__tagged_items__tag__name__in=tags
        ).values_list("event_id", flat=True)

        return Event.future_events.filter(
            Q(id__in=event_ids),
            location_query
        )

    def __unicode__(self):
        status = "QUEUE"
        if self.processed:
            status = "PROCESSED"
        return "%s - %s" % (self.event.name, status)


def add_to_in_the_loop_schedule(sender, instance, created, **kwargs):
    InTheLoopSchedule.objects.filter(event_id=instance.id).delete()
    InTheLoopSchedule(event=instance).save()


models.signals.post_save.connect(add_to_in_the_loop_schedule, sender=Event)


class ActiveVenueTypeManager(models.Manager):
    def get_query_set(self):
        return super(ActiveVenueTypeManager, self).get_query_set().filter(active=True)


class VenueType(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    active_types = ActiveVenueTypeManager()

    def __unicode__(self):
        return self.name


class VenueAccount(models.Model):
    venue = models.ForeignKey(Venue)
    phone = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(verbose_name='Custom Venue Fax', max_length=20, blank=True, null=True)
    email = models.EmailField(verbose_name='Custom Venue Email', blank=True, null=True)
    site = models.URLField(verbose_name='Custom Venue Website Address', blank=True, null=True)
    myspace = models.URLField(verbose_name='Custom Venue MySpace page', blank=True, null=True)
    facebook = models.URLField(verbose_name='Custom Venue Facebook page', blank=True, null=True)
    twitter = models.URLField(verbose_name='Custom Venue Twitter page', blank=True, null=True)
    account = models.ForeignKey(Account)
    about = models.TextField(verbose_name='Text for "About Us" block', blank=True, null=True)
    picture = ImageCropField(upload_to='venue_profile_imgs', blank=True, null=True, help_text='Custom Venue Profile picture')
    cropping = ImageRatioField('picture', '154x154', size_warning=True, allow_fullsize=True)
    slug = models.SlugField(verbose_name='Unique URL for custom Venue, created from name', unique=True)
    public = models.BooleanField(default=True)
    types = models.ManyToManyField(VenueType)

    def __unicode__(self):
        return self.venue.__unicode__()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = self.uniqueSlug()
        super(VenueAccount, self).save(*args, **kwargs)
        return self

    def uniqueSlug(self):
        """
        Returns: A unique (to database) slug name
        """
        suffix = 0
        potential = base = slugify(self.venue.name)
        while True:
            if suffix:
                potential = base + str(suffix)
            try:
                VenueAccount.objects.get(slug=potential)
            except ObjectDoesNotExist:
                return potential
            suffix = suffix + 1


class AccountTax(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    regions = models.ManyToManyField(Region)
    tax = models.DecimalField(max_digits=10, decimal_places=4)

    def __unicode__(self):
        return "%s(%s) %s" % (self.name, self.tax, self.regions.all())

    def pretty_tax(self):
        return "%g" % (self.tax*100) 
