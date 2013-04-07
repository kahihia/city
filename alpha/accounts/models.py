from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from django.contrib.gis.db import models
from taggit_autosuggest.managers import TaggableManager

from event.models import Event, SingleEvent

from phonenumber_field.modelfields import PhoneNumberField

from django_facebook.models import FacebookProfileModel

from django.db.models.signals import post_save

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

post_save.connect(create_facebook_profile, sender=User)
