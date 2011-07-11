from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import string
import sha
import random
from taggit.managers import TaggableManager

from PIL import Image

from Event.utils import picture_file_path
from Event import EVENT_RESIZE_METHOD, EVENT_PICTURE_DIR

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
    slug = models.SlugField(unique=True)
    # event picture
    picture = models.ImageField(upload_to=picture_file_path, blank=True, null=True, help_text='The event picture')
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

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.authentication_key = ''.join(random.choice(string.ascii_letters + '0123456789') for x in xrange(40) )
        
        self.slug = self.uniqueSlug()
        super(Event, self).save(*args, **kwargs)
        return self

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
        return os.path.join(EVENT_PICTURE_DIR, self.pk, 'resized_pic', 
                            str(size), self.image.name)

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
                                  

class Venue(models.Model):
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=200)
    latitude = models.DecimalField(decimal_places=2, max_digits=8)
    longitude = models.DecimalField(decimal_places=2, max_digits=8)
    country = models.CharField(max_length=200)

class CanadianVenue(Venue):
    province = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=50)
