from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist, ValidationError

import string
import sha
import random
from taggit.managers import TaggableManager
import os
import os.path
from PIL import Image
import datetime
from alpha.event import EVENT_PICTURE_DIR, EVENT_RESIZE_METHOD, EVENT_DEFAULT_SIZES
from StringIO import StringIO
from django.core.files.base import ContentFile
def picture_file_path(instance = None, filename = None):
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
        return u'%s %s' % (self.name, self.created)
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
    picture = models.ImageField(upload_to=picture_file_path, blank=True, null=True, help_text='The event picture')
    #--------------------------------------------------------------
    # View set fields - these are set in the view -----------------
    #==============================================================
    # the user which that created the event, or no event
    # only one user can own an event
    owner = models.ForeignKey(User, blank=True, null=True)
    # a recurrence is a set of events, combined with some user defined rule
    recurrence = models.ForeignKey('Recurrence', null=True, blank=True)
    #--------------------------------------------------------------
    # User set fields - these are input by the user and validated -
    #==============================================================
    email = models.CharField('email address',max_length=100)    # the event must have an email
    name = models.CharField('event title',max_length=250)    # the title of the event
    description = models.TextField(blank=True)    # the longer description of the event
    start_time = models.DateTimeField('starting time',auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField('ending time (optional)',auto_now=False, auto_now_add=False, blank=True, null=True)
    location = models.CharField('location of the event',max_length=500)
    venue = models.ForeignKey('CanadianVenue', blank=True, null=True)    # a specific venue associated with the event
    price = models.CharField('event price (optional)',max_length=40, blank=True, default='Free')
    website = models.URLField(verify_exists=False, blank=True, null=True, default='')
    #-------------------------------------------------------------
    # django-taggit field for tags--------------------------------
    #=============================================================
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.authentication_key = ''.join(random.choice(string.ascii_letters + '0123456789') for x in xrange(40) )
            self.slug = self.uniqueSlug()
        super(Event, self).save(*args, **kwargs)
        return self
    def clean(self):
        if self.end_time:
            if self.start_time > self.end_time:
                raise ValidationError('The event date and time must be later than the start date and time.')
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
                conflict = Event.events.get(slug=potential)
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
    
    def create_resized(self, size):
        """
        Creates a resized image on the filesystem using EVENT_RESIZE_METHOD
        Uses the self.picture_name method to determine the file path.

        Pre: No file exists
        Post: A resized file is created in the filesystem by the storage manager.
        Returns: Nothing
        """
        try:
            original = self.picture.storage.open(self.picture.name, 'rb').read()
            image = Image.open(StringIO(original))
        except IOError:
            picture_thumb = '' # we can't read the file, we don't have the codec support
            return
        #make the jpeg
        (width,height) = image.size
        if width != size or height != size:
            if width > height:
                difference = (width - height) / 2
                image = image.crop( (difference, # <-----------#\
                                     0,                         #\
                                     width - difference,         #\
                                     height)     # <------------- #\
                                    )                              #\
            else:                                                  #=-Symmetry is awesome
                difference = (height - width) / 2                  #/
                image = image.crop( (0,          # <--------------#/
                                     difference,                 #/
                                     width,                     #/
                                     height - difference) # <--#/
                                    )
            image = image.resize( (size, size),
                                  EVENT_RESIZE_METHOD
                                  )
            #convert to rgb
            if image.mode != 'RGB':
                image = image.convert('RGB')

            #make the jpeg
            resized_pic = StringIO()
            image.save(resized_pic, 'JPEG')
            resized_pic_file = ContentFile(resized_pic.getvalue())
        else:
            resized_pic_file = ContentFile(original)

        # save the jpeg
        thumb = self.picture.storage.save( self.picture_name(size),
                                           resized_pic_file )
 

def create_default_pictures(instance=None, created=False, **kwargs):
    """
    post_save

    django.db.models.signals.post_save

    Like pre_save, but sent at the end of the save() method.
    
    Arguments sent with this signal:

    sender
      The model class.

    instance
      The actual instance being saved.

    created
      A boolean; True if a new record was created.

    raw
      A boolean; True if the model is saved exactly as presented
      (i.e. when loading a fixture). One should not query/modify other
      records in the database as the database might not be in a
      consistent state yet.

    using
      The database alias being used. 

    """
    if created:
        for size in EVENT_DEFAULT_SIZES:
            instance.create_resized(size)
models.signals.post_save.connect(create_default_pictures, sender=Event)


class Venue(models.Model):
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=200)
    latitude = models.DecimalField(decimal_places=2, max_digits=8)
    longitude = models.DecimalField(decimal_places=2, max_digits=8)
    country = models.CharField(max_length=200)

class CanadianVenue(Venue):
    province = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=50)

class Recurrence(models.Model):
    pass
