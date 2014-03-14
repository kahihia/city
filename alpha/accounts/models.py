import datetime

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Count
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from cities.models import Region, City
from userena.models import UserenaBaseProfile
from django_facebook.models import FacebookProfileModel

from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager
from advertising.models import Advertising, AdvertisingCampaign
from image_cropping import ImageCropField, ImageRatioField
from taggit_autosuggest.managers import TaggableManager
from home.utils import deserialize_json_deep
from event.models import Event, SingleEvent, FeaturedEvent, Venue
from notices.models import Notice

REMINDER_TYPES = {
    'HOURS': {
        'id': 1,
        'title': 'Hours before event'
    },
    'DAYS': {
        'id': 2,
        'title': 'Days before event'
    },
    'WEEKDAY': {
        'id': 4,
        'title': 'On week day'
    },
    'EACH_DAY': {
        'id': 8,
        'title': 'Each day, starting from'
    }
}

DAYS_OF_WEEK = (
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
)

LOCATION_TYPES = (
    ('country', "Country"),
    ('region', "Teritory"),
    ('city', "City")
)


class AccountSettingsMixin(models.Model):
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPES, blank=True, null=True)
    location_name = models.CharField(max_length=256, blank=True, null=True)
    location_id = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class Account(UserenaBaseProfile, FacebookProfileModel, AccountSettingsMixin):
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='my_profile')
    
    tax_origin_confirmed = models.BooleanField(default=False)
    not_from_canada = models.BooleanField(default=False)
    native_region = models.ForeignKey(Region, blank=True, null=True, related_name="native_for_accounts")

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

    # remind each day, starting from
    reminder_each_day_from = models.IntegerField(blank=True, null=True)
    reminder_each_day_at_time = models.TimeField(blank=True, null=True)

    reminder_type_state = models.IntegerField(blank=True, null=False, default=REMINDER_TYPES['HOURS']['id'])

    # remind types

    reminder_with_website = models.BooleanField(default=True)
    reminder_with_email = models.BooleanField(default=True)
    reminder_with_sms = models.BooleanField(default=False)

    reminder_email = models.EmailField(blank=True, null=True)
    reminder_phonenumber = models.CharField(max_length=15, blank=True, null=True)

    # single events for remind
    reminder_single_events = models.ManyToManyField('event.SingleEvent', blank=True, null=True)

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

    bonus_budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    objects = models.Manager()
    accounts = money_manager(models.Manager())

    def future_events(self):        
        return SingleEvent.future_events.filter(event__owner_id=self.user.id)

    def featured_events(self):
        return FeaturedEvent.objects.filter(owner__id=self.id)

    def archived_events(self):
        return SingleEvent.archived_events.filter(event__owner_id=self.id)

    def in_the_loop_events(self):
        region_ids = self.regions.all().values_list("id", flat=True)
        city_ids = self.cities.all().values_list("id", flat=True)

        if self.all_of_canada:
            location_query = Q(event__venue__country__name="Canada")
        else:
            location_query = Q(event__venue__city__id__in=city_ids) | Q(event__venue__city__region__id__in=region_ids) | Q(event__venue__city__subregion__id__in=region_ids)

        return SingleEvent.future_events.filter(
            Q(event__tagged_items__tag__name__in=self.in_the_loop_tags.all().values_list("name", flat=True)),
            location_query
        ).annotate(Count("id"))


    def reminder_single_events_in_future(self):
        return SingleEvent.future_events.filter(id__in=self.reminder_single_events.values_list('id', flat=True))

    def ads(self):
        return Advertising.objects.filter(campaign__account__id=self.id)

    def campaigns(self):
        return AdvertisingCampaign.objects.filter(account__id = self.id)

    def taxes(self):
        if self.native_region:
            return AccountTax.objects.filter(regions__id=self.native_region.id)
        else:
            return []

    def reminder_weekday(self):
            return "%s" % dict(DAYS_OF_WEEK)[self.reminder_on_week_day]


    def in_the_loop_tag_names(self):
        return self.in_the_loop_tags.all().values_list("name", flat=True)

    def advertising_region(self):
        if self.not_from_canada:
            return None

        return self.native_region

    def shared_campaigns(self):
        return AdvertisingCampaign.objects.filter(
            Q(account=self) | Q(shareadvertisingcampaign__account=self)
        )

    def notices(self):
        return Notice.objects.filter(user__id=self.user.id, read=False).order_by('-id')

    def notices_history(self):
        return Notice.objects.filter(user__id=self.user.id).order_by('-id')

    def venues(self):
        return Venue.objects.filter(user=self.user, suggested=True)

    def check_reminder_type_state(self, type, state=None):
        if not state:
            state = self.reminder_type_state

        return bool(state & REMINDER_TYPES[type]['id'])


class RemindingManager(models.Manager):
    def get_query_set(self):
        return super(RemindingManager, self).get_query_set().filter(notification_time__lte=datetime.datetime.now(), done=False)

    def existing(self):
        return self.filter(single_event__isnull=False)

    def deleted(self):
        return self.filter(single_event__isnull=True)


NOTIFICATION_TYPES = (
    ('DAYS_BEFORE_EVENT', 'Days before event'),
    ('HOURS_BEFORE_EVENT', 'Hours before event'),
    ('ON_WEEK_DAY', 'On week day'),
    ('DELETED_EVENT', 'Deleted event'),
)


class AccountReminding(models.Model):
    account = models.ForeignKey(Account)
    single_event = models.ForeignKey('event.SingleEvent', blank=True, null=True)
    archived_data = models.TextField(blank=True, null=True)
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
        return "%s at (%s) - %s" % (self.title, self.notification_time, status)

    @property
    def title(self):
        if self.single_event:
            return self.single_event.name
        elif self.archived_data:
            single_event = deserialize_json_deep(self.archived_data, {'event': {'relations': ('venue',)}})[0]
            return single_event.name
        else:
            return ''


class NewInTheLoopEventManager(models.Manager):
    def get_query_set(self):
        return super(NewInTheLoopEventManager, self).get_query_set().filter(processed=False)


class InTheLoopSchedule(models.Model):
    event = models.ForeignKey('event.Event')
    processed = models.BooleanField(default=False)

    objects = models.Manager()
    new_events = NewInTheLoopEventManager()

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
        ).annotate(repeat_count=Count('id'))


    def process(self):
        InTheLoopSchedule.objects.filter(id=self.id).update(processed=True)

    @staticmethod
    def process_events(events):
        InTheLoopSchedule.objects.filter(id__in=events).update(processed=True)
        

    def __unicode__(self):
        status = "QUEUE"
        if self.processed:
            status = "PROCESSED"
        return "%s - %s" % (self.event.name, status)


def add_to_in_the_loop_schedule(sender, instance, created, **kwargs):
    if created:
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


class PublicVenueManager(models.Manager):
    def get_query_set(self):
        return super(PublicVenueManager, self).get_query_set().filter(public=True)

    def filter_by_location(self, location_type, location_id):
        if location_type == 'country':
            return self._filter_by_country(location_id)
        elif location_type == 'region':
            return self._filter_by_region(location_id)
        elif location_type == 'city':
            return self._filter_by_city(location_id)
        else:
            return self

    def _filter_by_country(self, id):
        return self.filter(venue__country__id=id)

    def _filter_by_region(self, id):
        return self.filter(Q(venue__city__region__id=id) | Q(venue__city__subregion__id=id))

    def _filter_by_city(self, id):
        return self.filter(venue__city__id=id)


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
    slug = models.SlugField(verbose_name='Unique URL for custom Venue, created from name', max_length=255, unique=True)
    public = models.BooleanField(default=True)
    types = models.ManyToManyField(VenueType)

    viewed = models.IntegerField(default=0)

    tags = TaggableManager()

    objects = models.Manager()
    public_venues = PublicVenueManager()

    def __unicode__(self):
        return self.venue.__unicode__()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = self.uniqueSlug()
        super(VenueAccount, self).save(*args, **kwargs)
        return self

    def get_absolute_url(self):
        if self.public:
            return reverse('public_venue_account', kwargs={'slug': self.slug})
        else:
            return reverse('private_venue_account', kwargs={'slug': self.slug})

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

    def ads(self):
        return Advertising.objects.filter(campaign__venue_account__id=self.id)

    def campaigns(self):
        return AdvertisingCampaign.objects.filter(venue_account__id=self.id)

    def view(self):
        VenueAccount.objects.filter(id=self.id).update(viewed=F("viewed")+1)

    def short_description(self):
        description = strip_tags(self.about)
        if len(description) > 255:
            return '%s...' % description[:255]

        return description

    @property
    def social_links(self):
        return self.venueaccountsociallink_set.all()

    @property
    def tags_as_string(self):
        return ', '.join([tag.name for tag in self.tags.all()])


class VenueAccountSocialLink(models.Model):
    venue_account = models.ForeignKey(VenueAccount)
    title = models.CharField(max_length=255)
    link = models.URLField()

    def __unicode__(self):
        return "%s - %s" % (self.title, self.link)


class AccountTax(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    regions = models.ManyToManyField(Region)
    tax = models.DecimalField(max_digits=10, decimal_places=4)

    def __unicode__(self):
        return "%s(%s) %s" % (self.name, self.tax, self.regions.all())

    def pretty_tax(self):
        return "%g" % (self.tax*100)


class AccountTaxCost(models.Model):
    account_tax = models.ForeignKey(AccountTax)
    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    tax_name = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s: %s" % (self.account_tax, self.cost)


class OccurringBonusesManager(models.Manager):
    def get_query_set(self):
        now = datetime.datetime.now()
        return super(OccurringBonusesManager, self).get_query_set()\
            .filter(start_time__lte=now, end_time__gte=now)


class BonusCampaign(models.Model):
    start_time = models.DateTimeField('starting time', auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField('ending time', auto_now=False, auto_now_add=False)

    budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    apply_to_old_accounts = models.BooleanField(default=False)

    occurring_bonuses = OccurringBonusesManager()
    objects = models.Manager()

    def __unicode__(self):
        return "Bonus %s(%s-%s)" % (self.budget, self.start_time, self.end_time)