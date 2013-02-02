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

    events = models.Manager()
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

    def picture_exists(self, size):
        """
        Returns: True or False, the status of a size of picture. Used
                 to tell if we need to create one.
        """
        return self.picture.storage.exists(self.picture_name(size))

    def picture_name(self, size):
        """
        Returns: The file name of the picture of a given size.
        """
        return os.path.join(EVENT_PICTURE_DIR, str(self.pk), 'resized_pic',
                            str(size), os.path.basename(self.picture.name))

    def picture_url(self, size):
        """
        Returns: The url of the picture of a certain size.
        """
        return self.picture.storage.url(self.picture_name(size))


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
    event = models.ForeignKey(Event, blank=False, null=False)
    start_time = models.DateTimeField('starting time', auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField('ending time (optional)', auto_now=False, auto_now_add=False)
    description = models.TextField(null=True, blank=True)  # additional description


class Venue(models.Model):
    name = models.CharField(max_length=250, default='Default Venue')
    street = models.CharField(max_length=250, blank=True)
    city = models.ForeignKey(City)
    location = models.PointField()
    country = models.ForeignKey(Country)
    objects = models.GeoManager()

    def __unicode__(self):
        return "%s, %s, %s" % (self.name, self.street, self.city)


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

    return "(%s)" % phrases


class AuditEvent(Event):
    phrases = models.ManyToManyField(AuditPhrase)


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
    name_search_result = re.findall(bad_phrases, instance.name)
    description_search_result = re.findall(bad_phrases, instance.description)
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

        subject = 'Bad phrases are catching'

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
        msg.send()

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
