from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import URLValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from cities.models import City, Country
import string
import random
from taggit_autosuggest.managers import TaggableManager
import os

import datetime
from .settings import EVENT_PICTURE_DIR

from image_cropping import ImageCropField, ImageRatioField

from django.db.models import Min, Max, Count, Q, F

from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager

from mamona import signals
from mamona.models import build_featured_event_payment_model
from decimal import Decimal
from ckeditor.fields import RichTextField


def picture_file_path(instance=None, filename=None):
    """
    This is used by the model and is defined in the Django
    documentation as a function which is used by the upload_to karg of
    an ImageField I will copy the relevant documentation here from
    FileField.upload_to:

    This may also be a callable, such as a function, which will be
    called to obtain the upload path, including the filename. This
    callable must be able to accept two arguments, and return a
    Unix-style path (with forward slashes) to be passed along to the
    storage system. The two arguments that will be passed are:

    Argument      Description

    ------------------------------------------------------------------

    instance      An instance of the model where the
                  FileField is defined. More specifically, this is
                  the particular instance where the current file is
                  being attached.

                  In most cases, this object will not have been saved
                  to the database yet, so if it uses the default
                  AutoField, it might not yet have a value for its
                  primary key field.

    filename 	  The filename that was originally given to the
                  file. This may or may not be taken into account
                  when determining the final destination path.

    Also has one optional argument: FileField.storage, a storage
    object, which handles the storage and retrieval of your files.
    """
    return os.path.join(EVENT_PICTURE_DIR, datetime.date.today().isoformat(), filename)


EVENT_TYPES = (
    ('SINGLE', 'Single'),
    ('MULTIDAY', 'Multiday'),
    ('MULTITIME', 'Multitime'),
)


def has_changed(instance, field):
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.filter(pk=instance.pk).values(field).get()[field]

    return not getattr(instance, field) == old_value    


class FutureManager(models.Manager):
    def get_query_set(self):
        queryset = super(FutureManager, self).get_query_set()\
            .filter(single_events__start_time__gte=datetime.datetime.now())\
            .select_related('single_events')\
            .select_related('single_events__occurrences')\
            .annotate(start_time=Min("single_events__start_time"))\
            .annotate(end_time=Min("single_events__end_time"))\
            .extra(order_by=['start_time'])\
            .annotate(Count("id"))

        return queryset

# manager will help me to outflank django restriction https://code.djangoproject.com/ticket/13363
class FutureWithoutAnnotationsManager(models.Manager):
    def get_query_set(self):
        queryset = super(FutureWithoutAnnotationsManager, self).get_query_set()\
            .filter(single_events__start_time__gte=datetime.datetime.now())\
            .select_related('single_events')
        return queryset


class FeaturedManager(models.Manager):
    def get_query_set(self):        
        return super(FeaturedManager, self).get_query_set()\
            .filter(
                single_events__start_time__gte=datetime.datetime.now(),
                featuredevent__start_time__lte=datetime.datetime.now(),
                featuredevent__end_time__gte=datetime.datetime.now(),
                featuredevent__active=True
            )\
            .annotate(start_time=Min("single_events__start_time"))\
            .annotate(end_time=Min("single_events__end_time"))\
            .annotate(Count("id"))


class ArchivedManager(models.Manager):
    def get_query_set(self):
        queryset = super(ArchivedManager, self).get_query_set()\
            .exclude(single_events__start_time__gte=datetime.datetime.now())\
            .select_related('single_events')\
            .annotate(start_time=Max("single_events__start_time"))\
            .annotate(end_time=Max("single_events__end_time"))\
            .extra(order_by=['-start_time'])\
            .annotate(Count("id"))

        return queryset


class Event(models.Model):
    class Meta:
        verbose_name_plural = 'Events'

    def __unicode__(self):
        return u'%s/// %s' % (self.owner, self.name)    

    events = models.Manager()

    future_events = FutureManager()
    future_events_without_annotation = FutureWithoutAnnotationsManager()
    featured_events = FeaturedManager()
    archived_events = ArchivedManager()

    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    modified = models.DateTimeField(auto_now=True, default=datetime.datetime.now())

    authentication_key = models.CharField(max_length=40)
    slug = models.SlugField(unique=True, max_length=255)

    picture = ImageCropField(upload_to=picture_file_path, blank=True, null=True, help_text='The event picture')
    cropping = ImageRatioField('picture', '180x180', size_warning=True, allow_fullsize=True)
    
    owner = models.ForeignKey(User, blank=True, null=True)
    venue_account_owner = models.ForeignKey('accounts.VenueAccount', blank=True, null=True, on_delete=models.SET_NULL)
    
    email = models.CharField('email address', max_length=100)
    name = models.CharField('event title', max_length=250)
    description = RichTextField(blank=True)
    location = models.PointField()
    venue = models.ForeignKey('Venue', blank=True, null=True)
    price = models.CharField('event price (optional)', max_length=40, blank=True, default='Free')
    website = models.URLField(blank=True, null=True, default='')
    tickets = models.CharField('tickets', max_length=250, blank=True, null=True)

    post_to_facebook = models.BooleanField(default=False, blank=True)
    comment_for_facebook = models.CharField(max_length=255, blank=True, null=True)

    audited = models.BooleanField(default=False)

    viewed_times = models.IntegerField(default=0, blank=True, null=True)

    facebook_event = models.ForeignKey('FacebookEvent', blank=True, null=True)

    event_type = models.CharField(max_length=10, choices=EVENT_TYPES, default="SINGLE")

    tags = TaggableManager()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.authentication_key = ''.join(random.choice(string.ascii_letters + '0123456789') for x in xrange(40))
            self.slug = self.uniqueSlug()

        if has_changed(self, 'name'):
            self.slug = self.uniqueSlug()

        super(Event, self).save(*args, **kwargs)
        return self

    def tags_representation(self):
        return ", ".join([tag.name for tag in self.tags.all()])

    def clean(self):
        if self.name and slugify(self.name) == '':
            raise ValidationError('Please enter a name for your event.')

    def uniqueSlug(self):
        """
        Returns: A unique (to database) slug name
        """
        suffix = 0
        potential = base = slugify(self.name)
        while True:
            if suffix:
                potential = base + str(suffix)
            try:
                Event.events.get(slug=potential)
            except ObjectDoesNotExist:
                return potential
            suffix = suffix + 1

    def is_featured(self):
        return self.featuredevent_set.filter(
            start_time__lte=datetime.datetime.now(),
            end_time__gte=datetime.datetime.now(),
            active=True
        ).count() > 0

    def is_tickets_representet_with_url(self):
        url_validator = URLValidator()
        try:
            url_validator(self.tickets)
            return True
        except ValidationError:
            return False

    def next_day(self):
        try:
            return SingleEvent.objects.filter(start_time__gte=datetime.datetime.now(), event=self).order_by("start_time")[0]
        except:
            return None

    def base(self):
        return self

    def event_identifier(self):
        return self.id

    def event_description(self):
        return self.description

    def is_fb_posted(self):
        return self.post_to_facebook and self.facebook_event

    @staticmethod
    def featured_events_for_region(region):
        if region:
            region_id = region.id
        else:
            region_id = None

        return Event.featured_events.filter(
            Q(featuredevent__all_of_canada=True) | Q(featuredevent__regions__id=region_id)
        ).order_by('?').annotate(Count("id"))


class FutureEventDayManager(models.Manager):
    def get_query_set(self):
        now = datetime.datetime.now()
        return super(FutureEventDayManager, self).get_query_set()\
            .filter(Q(start_time__gte=now) or Q(occurrences__start_time__gte=now))\
            .select_related('event')\
            .select_related('occurrences')\
            .prefetch_related('event__venue')\
            .prefetch_related('event__venue__city')\
            .order_by("start_time")\
            .annotate(Count("id"))


class SingleEventOccurrence(models.Model):
    """
    When user create event he can choose one of event types.
    1. Single Event. User can choose different days. All this days will saved as SingleEvent instance
    2. Multiple Day Event. User can choose different time for every day. We create one SingleEvent that will start on start time of first day and will finish on finish time of last day.
    Time for each day will be saved in SingleEventOccurance instance.
    3. Multiple Time Event. User can choose one day and few times for it. Day will be saved as SingleEvent instance. Each time will be saved as SingleEventOccurance instance.
    """
    start_time = models.DateTimeField('starting time', auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField('ending time (optional)', auto_now=False, auto_now_add=False)
    description = models.TextField(null=True, blank=True)            


class SingleEvent(models.Model):
    """
        Single event is event that occur only once.
        So when we create Event that occur more then one time,
        for it automaticaly will be created single events.
    """
    class Meta:
        verbose_name_plural = 'Single events'

    def __unicode__(self):
        return u'%s/// %s' % (self.event, self.start_time)

    objects = models.Manager()

    future_events = FutureEventDayManager()

    event = models.ForeignKey(Event, blank=False, null=False, related_name='single_events')
    start_time = models.DateTimeField('starting time', auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField('ending time (optional)', auto_now=False, auto_now_add=False)
    description = models.TextField(null=True, blank=True)

    occurrences = models.ManyToManyField(SingleEventOccurrence, blank=True, null=True)

    def event_description(self):
        description = self.description
        if not description:
            description = self.event.description
        return description

    def __getattr__(self, key):
        if key not in ('event', '_event_cache'):
            return getattr(self.event, key)      
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, key))

    def event_identifier(self):
        return self.event.id

    def base(self):
        return self.event

    def first_occurrence(self):
        occurrences = self.occurrences.all()
        first_occurrence = None
        for occurence in occurrences:
            if not first_occurrence or first_occurrence.start_time > occurence.start_time:
                first_occurrence = occurence
        return first_occurrence

    def last_occurrence(self):
        occurrences = self.occurrences.all()
        last_occurrence = None
        for occurence in occurrences:
            if not last_occurrence or last_occurrence.start_time < occurence.start_time:
                last_occurrence = occurence
        return last_occurrence

    def sorted_occurrences(self):
        occurrences = self.occurrences.all()
        return sorted(occurrences, key=lambda occurrence: occurrence.start_time)


class FacebookEvent(models.Model):
    eid = models.BigIntegerField(blank=False, null=False)


def without_empty(array):
    return [x for x in array if x]


class Venue(models.Model):
    name = models.CharField(max_length=250, default='Default Venue')
    street = models.CharField(max_length=250, blank=True)
    street_number = models.CharField(max_length=250, blank=True)
    city = models.ForeignKey(City)
    location = models.PointField()
    country = models.ForeignKey(Country)
    suggested = models.BooleanField(default=False)
    objects = models.GeoManager()

    def __unicode__(self):
        street_str = " ".join(without_empty([self.street_number, self.street]))
        return ", ".join(without_empty([self.name, street_str, self.city.name]))

    def future_events(self):
        return Event.future_events.filter(venue__id=self.id)

    @staticmethod
    def with_active_events():
        ids = list(set(Event.future_events.values_list('venue__id', flat=True)))
        return Venue.objects.filter(id__in=ids)


class CountryBorder(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField('2 Digit ISO', max_length=2)
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

countryborders_mapping = {
    'code' : 'ISO2',
    'name' : 'NAME',        
    'mpoly' : 'MULTIPOLYGON',
}


class AuditPhrase(models.Model):
    phrase = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.phrase


def phrases_query():
    phrases = AuditPhrase.objects.filter(active=True)
    phrases = [pm.phrase for pm in phrases]
    phrases = "|".join(phrases)

    return r"(%s)" % phrases


class AuditEvent(Event):
    phrases = models.ManyToManyField(AuditPhrase)

    def phrases_list(self):
        return [phrase.phrase for phrase in self.phrases.all()]


class FakeAuditEvent(models.Model):
    event_ptr_id = models.PositiveIntegerField(db_column="event_ptr_id", primary_key=True)

    class Meta:
        app_label = AuditEvent._meta.app_label
        db_table = AuditEvent._meta.db_table
        managed = False


class AuditSingleEvent(models.Model):
    phrases = models.ManyToManyField(AuditPhrase)


class FutureFeaturedEventManager(models.Manager):
    def get_query_set(self):
        return super(FutureFeaturedEventManager, self).get_query_set()\
            .filter(event__single_events__start_time__gte=datetime.datetime.now())\
            .annotate(Count("id"))


class FeaturedEvent(models.Model):
    event = models.ForeignKey(Event, blank=False, null=False)
    owner = models.ForeignKey("accounts.Account", blank=True, null=True)
    start_time = models.DateTimeField('starting time')
    end_time = models.DateTimeField('ending time', auto_now=False, auto_now_add=False)
    active = models.BooleanField(default=False)
    owned_by_admin = models.BooleanField(default=False)

    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    all_of_canada = models.BooleanField(default=True)
    regions = models.ManyToManyField("cities.Region")

    objects = money_manager(models.Manager())
    future = FutureFeaturedEventManager()

    def __unicode__(self):
        return self.event.name

    def click(self):
        FeaturedEvent.objects.filter(id=self.id).update(clicks=F("clicks")+1)


    def view(self):
        FeaturedEvent.objects.filter(id=self.id).update(views=F("views")+1)

    def event_day(self):
        return Event.future_events.get(id=self.event.id)        


class FeaturedEventOrder(models.Model):
    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    total_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD') # with taxes
    featured_event = models.ForeignKey(FeaturedEvent)
    account = models.ForeignKey('accounts.Account')

    status = models.CharField(
            max_length=1,
            choices=(('s', 'success'), ('f', 'failure'), ('p', 'incomplete')),
            blank=True,
            default=''
    )

    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    taxes = models.ManyToManyField("accounts.AccountTaxCost")

    def __unicode__(self):
        return "Order to make %s featured from %s to %s" % (self.featured_event, self.featured_event.start_time.date(), self.featured_event.end_time.date())

    @property
    def cost_value(self):
        return self.cost

FeaturedEventPayment = build_featured_event_payment_model(FeaturedEventOrder, unique=True)

def get_items(self):
        """Retrieves item list using signal query. Listeners must fill
        'items' list with at least one item. Each item is expected to be
        a dictionary, containing at least 'name' element and optionally
        'unit_price' and 'quantity' elements. If not present, 'unit_price'
        and 'quantity' default to 0 and 1 respectively.

        Listener is responsible for providing item list with sum of prices
        consistient with Payment.amount. Otherwise the final amount may
        differ and lead to unpredictable results, depending on the backend used.
        """
        items = []
        signals.order_items_query.send(sender=type(self), instance=self, items=items)

        items.append({
            "unit_price": self.order.cost.amount,
            "name": self.order,
            "quantity": 1
        })

        for tax in self.order.account.taxes():
            items.append({
                "unit_price": (self.order.cost.amount * tax.tax).quantize(Decimal("0.01")),
                "name": tax.name,
                "quantity": 1
            })
        
        return items
FeaturedEventPayment.get_items = get_items

import listeners
