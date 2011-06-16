from django.db import models
from django.contrib.auth.models import User

import sha
import random


# Create your models here.

class Event(models.Model):
    # by default, the model has an id = models.AutoField(primary_key=True)
    # The manager is the interface for making database query operations on all models
    # example usage: Event.events.all() will provide a list of all event objects
    events = models.Manager()

    # private key...
    authentication_key = models.CharField(_('authentication key'), max_length=40)

    # public key
    public_key = models.CharField(_('public key'), max_length=40)

    # the user which that created the event, or no event
    # only one user can own an event
    owner = models.ForeignKey(User, blank=True)

    # the title of the event
    name = models.CharField(max_length=500)
    # the longer description of the event
    description = models.TextField(blank=True)
    # the time at which the event starts, in UTC
    # stored as a combined date and time
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    # the time at which the event will end, in UTC
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True)
    # the location that the event will be held
    location = models.CharField(max_length=500)  
    # a specific address of the event
    # represented by a model defined in this app
    venue = models.ForeignKey('Venue')
    
    # django-taggit field for tags
    # TODO

    # Future possible fields (present in facebook model):
    #  privacy
    #  update_timestamp
    #  feed
    #  noreply
    #  maybe
    #  invited
    #  attending
    #  declined
    #  picture


class Venue(models.Model):
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=200)
    province = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=50)
    country = models.CharField(max_length=200)
    latitude = models.DecimalField(decimal_places=2, max_digits=8)
    longitude = models.DecimalField(decimal_places=2, max_digits=8)
