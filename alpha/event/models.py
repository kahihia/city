from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import URLValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.template.loader import render_to_string

from django.conf import settings
from django.core.mail.message import EmailMessage

from cities.models import City, Country
import string
import random
from taggit_autosuggest.managers import TaggableManager
import os
import os.path
import re

import datetime
from event import EVENT_PICTURE_DIR

from image_cropping import ImageCropField, ImageRatioField

from djorm_pgfulltext.models import SearchManagerMixIn, SearchManager
from djorm_pgfulltext.fields import VectorField

from django.db.models import Min

from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager

from mamona import signals
from mamona.models import build_featured_event_payment_model
from decimal import Decimal
from ckeditor.fields import RichTextField


class SearchGeoDjangoManager(SearchManagerMixIn, models.GeoManager):
    pass


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


class FutureManager(SearchManager):
    def get_query_set(self):
        queryset = super(FutureManager, self).get_query_set()\
            .filter(single_events__start_time__gte=datetime.datetime.now())\
            .select_related('single_events')\
            .annotate(start_time=Min("single_events__start_time"))\
            .annotate(end_time=Min("single_events__end_time"))\
            .order_by("single_events__start_time")

        return queryset

# manager will help me to outflank django restriction https://code.djangoproject.com/ticket/13363
class FutureWithoutAnnotationsManager(SearchManager):
    def get_query_set(self):
        queryset = super(FutureWithoutAnnotationsManager, self).get_query_set()\
            .filter(single_events__start_time__gte=datetime.datetime.now())\
            .select_related('single_events')
        return queryset


class FeaturedManager(FutureManager):
    def get_query_set(self):
        return super(FeaturedManager, self).get_query_set()\
            .filter(
                featuredevent__start_time__lte=datetime.datetime.now(),
                featuredevent__end_time__gte=datetime.datetime.now(),
                featuredevent__active=True
            )

class ArchivedManager(SearchManager):
    def get_query_set(self):
        queryset = super(ArchivedManager, self).get_query_set()\
            .filter(single_events__start_time__lte=datetime.datetime.now())\
            .select_related('single_events')\
            .annotate(start_time=Min("single_events__start_time"))\
            .annotate(end_time=Min("single_events__end_time"))\
            .order_by("-single_events__start_time")

        return queryset


class Event(models.Model):
    class Meta:
        verbose_name_plural = 'Events'

    def __unicode__(self):
        return u'%s/// %s' % (self.owner, self.name)    

    events = SearchManager(
        fields=('name', 'description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True
    )

    future_events = FutureManager(
        fields=('name', 'description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True)

    future_events_without_annotation = FutureWithoutAnnotationsManager(
        fields=('name', 'description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True)

    featured_events = FeaturedManager(
        fields=('name', 'description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True)

    archived_events = ArchivedManager(
        fields=('name', 'description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True)


    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    modified = models.DateTimeField(auto_now=True, default=datetime.datetime.now())

    authentication_key = models.CharField(max_length=40)
    slug = models.SlugField(unique=True, max_length=255)

    picture = ImageCropField(upload_to=picture_file_path, blank=True, null=True, help_text='The event picture')
    cropping = ImageRatioField('picture', '180x180', size_warning=True, allow_fullsize=True)
    
    owner = models.ForeignKey(User, blank=True, null=True)
    venue_account_owner = models.ForeignKey('accounts.VenueAccount', blank=True, null=True)
    
    email = models.CharField('email address', max_length=100)
    name = models.CharField('event title', max_length=250)
    description = RichTextField(blank=True)
    location = models.PointField()
    venue = models.ForeignKey('Venue', blank=True, null=True)
    price = models.CharField('event price (optional)', max_length=40, blank=True, default='Free')
    website = models.URLField(blank=True, null=True, default='')
    tickets = models.CharField('tickets', max_length=250, blank=True, null=True)

    audited = models.BooleanField(default=False)

    viewed_times = models.IntegerField(default=0, blank=True, null=True)

    search_index = VectorField()

    tags = TaggableManager()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.authentication_key = ''.join(random.choice(string.ascii_letters + '0123456789') for x in xrange(40))
            self.slug = self.uniqueSlug()
        super(Event, self).save(*args, **kwargs)
        return self

    def tags_representation(self):
        return ", ".join([tag.name for tag in self.tags.all()])

    def clean(self):
        #if self.end_time:
        #    if self.start_time > self.end_time:
        #        raise ValidationError('The event date and time must be later than the start date and time.')
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

    def start_time(self):
        next_day = self.next_day()
        if next_day:
            return next_day.start_time
        else:
            return None

    def end_time(self):
        next_day = self.next_day()
        if next_day:
            return next_day.end_time
        else:
            return None

    def event_identifier(self):
        return self.id

    def event_description(self):
        return self.description


class FutureEventDayManager(models.Manager):
    def get_query_set(self):
        return super(FutureEventDayManager, self).get_query_set()\
            .filter(start_time__gte=datetime.datetime.now())\
            .select_related('event')\
            .order_by("start_time")


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
    description = models.TextField(null=True, blank=True)  # additional description
    search_index = VectorField()

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


class Venue(models.Model):
    name = models.CharField(max_length=250, default='Default Venue')
    street = models.CharField(max_length=250, blank=True)
    city = models.ForeignKey(City)
    location = models.PointField()
    country = models.ForeignKey(Country)
    objects = models.GeoManager()

    def __unicode__(self):
        return "%s, %s, %s" % (self.name, self.street, self.city)

    def future_events(self):
        return Event.future_events.filter(venue__id=self.id)

    @staticmethod
    def with_active_events():
        ids = list(set(Event.future_events.values_list('venue__id', flat=True)))
        return Venue.objects.filter(id__in=ids)


class CanadianVenue(Venue):
    province = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=50)


class Reminder(models.Model):
    email = models.CharField(max_length=100)
    date = models.DateTimeField()
    event = models.CharField(max_length=100)

    def __unicode__(self):
        return self.event


class AuditPhrase(models.Model):
    phrase = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.phrase


def phrases_query():
    # TODO: add caching
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

        current_site = settings.EVENT_EMAIL_SITE

        subject = 'Bad phrases have been caught!'

        message = render_to_string('audit/bad_phrases_email.txt', {
            'site': current_site,
            'event': audit_event,
            'phrases': phrases
        })

        msg = EmailMessage(subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                map(lambda x: x[1], settings.ADMINS))

        msg.content_subtype = 'html'


models.signals.post_save.connect(audit_event_catch, sender=Event)

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


class FeaturedEvent(models.Model):
    event = models.ForeignKey(Event, blank=False, null=False)
    owner = models.ForeignKey("accounts.Account", blank=True, null=True)
    start_time = models.DateTimeField('starting time')
    end_time = models.DateTimeField('ending time', auto_now=False, auto_now_add=False)
    active = models.BooleanField(default=False)

    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    objects = money_manager(models.Manager())

    def __unicode__(self):
        return self.event.name

    def click(self):
        # TODO: calculate cost
        self.clicks = self.clicks + 1
        self.save()

    def view(self):
        self.views = self.views + 1
        self.save()


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

    def __unicode__(self):
        return "Order to make %s featured from %s to %s" % (self.featured_event, self.featured_event.start_time.date(), self.featured_event.end_time.date())

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
