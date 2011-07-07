from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import string
import sha
import random
from taggit.managers import TaggableManager

class Event(models.Model):
    class Meta:
        verbose_name_plural = 'Events'
    #--------------------------------------------------------------
    # Django set fields - these are set by django -----------------
    #==============================================================
    # id = models.AutoField(primary_key=True)

    # The manager is the interface for making database query operations on all models
    # example usage: Event.events.all() will provide a list of all event objects
    events = models.Manager()
 
    #--------------------------------------------------------------
    # Save set fields - these are set in the save -----------------
    #==============================================================
    # private key
    authentication_key = models.CharField(max_length=40)
    # public key is a 'slug' generated from the name of the event
    slug = models.SlugField()
    # event picture
    picture = models.ImageField(upload_to='pictures', blank=True, null=True, help_text='The event picture')
    picture_thumb = models.ImageField(upload_to='pictures_thumb', blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.authentication_key = ''.join(random.choice(string.ascii_letters + '0123456789') for x in xrange(40) )
        self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)
        return self

    #--------------------------------------------------------------
    # View set fields - these are set in the view -----------------
    #==============================================================
    # the user which that created the event, or no event
    # only one user can own an event
    owner = models.ForeignKey(User, blank=True, null=True)

    #--------------------------------------------------------------
    # User set fields - these are input by the user and validated -
    #==============================================================
    email = models.CharField('email address',max_length=100)    # the event must have an email
    name = models.CharField('event title',max_length=255)    # the title of the event
    description = models.TextField(blank=True)    # the longer description of the event
    start_time = models.DateTimeField('starting time',auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField('ending time (optional)',auto_now=False, auto_now_add=False, blank=True, null=True)
    location = models.CharField('location of the event',max_length=500)
    venue = models.ForeignKey('CanadianVenue', blank=True, null=True)    # a specific venue associated with the event
    price = models.CharField('event price (optional)',max_length=40, blank=True, default='Free')

    #-------------------------------------------------------------
    # django-taggit field for tags--------------------------------
    #=============================================================
    tags = TaggableManager()

class Venue(models.Model):
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=200)
    latitude = models.DecimalField(decimal_places=2, max_digits=8)
    longitude = models.DecimalField(decimal_places=2, max_digits=8)
    country = models.CharField(max_length=200)

class CanadianVenue(Venue):
    province = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=50)
