from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
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


# class FutureManager(models.Manager):
#     def get_query_set(self):
#         return super(FutureManager, self).get_query_set().filter(single_events__start_time__gte=datetime.datetime.now())


# class FeaturedManager(FutureManager):
#     def get_query_set(self):
#         return super(FeaturedManager, self).get_query_set().filter(featured=True).order_by("featured_on")


class Event(models.Model):
    class Meta:
        verbose_name_plural = 'Events'

    def __unicode__(self):
        return u'%s/// %s' % (self.owner, self.name)
    #--------------------------------------------------------------
    # Django set fields - these are set by django -----------------
    #==============================================================
    # id = models.AutoField(primary_key=True)

    # The manager is the interface for making database query operations on all models
    # example usage: Event.events.all() will provide a list of all event objects

    events = SearchManager(
        fields=('name', 'description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True
    )
    # future_events = FutureManager()
    # featured_events = FeaturedManager()
    # timestamps
    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    modified = models.DateTimeField(auto_now=True, default=datetime.datetime.now())
    #--------------------------------------------------------------
    # Save set fields - these are set in the save -----------------
    #==============================================================
    # private key
    authentication_key = models.CharField(max_length=40)
    # public key is a 'slug' generated from the name of the event
    slug = models.SlugField(unique=True, max_length=255)
    # event picture
    picture = ImageCropField(upload_to=picture_file_path, blank=True, null=True, help_text='The event picture')
    cropping = ImageRatioField('picture', '180x180', size_warning=True, allow_fullsize=True)
    #--------------------------------------------------------------
    # View set fields - these are set in the view -----------------
    #==============================================================
    # the user which that created the event, or no event
    # only one user can own an event
    owner = models.ForeignKey(User, blank=True, null=True)
    # a recurrence is a set of events, combined with some user defined rule
    #commented by Arlus
    #recurrence = models.ForeignKey('Recurrence', null=True, blank=True)
    #--------------------------------------------------------------
    # User set fields - these are input by the user and validated -
    #==============================================================
    email = models.CharField('email address', max_length=100)  # the event must have an email
    name = models.CharField('event title', max_length=250)  # the title of the event
    description = models.TextField(blank=True)  # the longer description of the event
    location = models.PointField()
    venue = models.ForeignKey('Venue', blank=True, null=True)    # a specific venue associated with the event
    price = models.CharField('event price (optional)', max_length=40, blank=True, default='Free')
    website = models.URLField(blank=True, null=True, default='')
    tickets = models.CharField('tickets', max_length=250, blank=True, null=True)

    audited = models.BooleanField(default=False)

    # featured_on need to be set, when we add event to featured list
    featured = models.BooleanField(default=False)
    featured_on = models.DateTimeField('featured on', auto_now=False, auto_now_add=False, blank=True, null=True)

    viewed_times = models.IntegerField(default=0, blank=True, null=True)

    search_index = VectorField()

    #-------------------------------------------------------------
    # django-taggit field for tags--------------------------------
    #=============================================================
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

    def next_day(self):
        return SingleEvent.objects.filter(start_time__gte=datetime.datetime.now(), event=self).order_by("start_time")[0]


class FutureManager(SearchManager):
    def get_query_set(self):
        return super(FutureManager, self).get_query_set().filter(start_time__gte=datetime.datetime.now())


class FeaturedManager(FutureManager):
    def get_query_set(self):
        return super(FeaturedManager, self).get_query_set().filter(event__featured=True).order_by("event__featured_on")


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

    future_events = FutureManager(fields=('description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True)

    featured_events = FeaturedManager(fields=('description'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True)

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


class VenueWithActiveEventsManager(models.GeoManager):
    def get_query_set(self):
        ids = list(set(SingleEvent.future_events.values_list('event__venue__id', flat=True)))
        return super(models.GeoManager, self).get_query_set().\
            filter(id__in=ids)


class Venue(models.Model):
    name = models.CharField(max_length=250, default='Default Venue')
    street = models.CharField(max_length=250, blank=True)
    city = models.ForeignKey(City)
    location = models.PointField()
    country = models.ForeignKey(Country)
    objects = models.GeoManager()

    with_active_events = VenueWithActiveEventsManager()

    def __unicode__(self):
        return "%s, %s, %s" % (self.name, self.street, self.city)

    def future_events(self):
        return SingleEvent.future_events.filter(event__venue=self.id).order_by("start_time")


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
        #msg.send()

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
