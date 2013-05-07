#!/usr/bin/env python
#-*-coding: UTF-8-*-

from django.db import models

from event.models import Venue
from django.contrib.auth.models import User
from accounts.models import Account
from image_cropping import ImageCropField, ImageRatioField
from event.models import Event

class VenueProfile(Venue):
    cv_phone = models.CharField(verbose_name = 'Custom Venue Phone', max_length = 20)
    cv_fax = models.CharField(verbose_name = 'Custom Venue Fax', max_length = 20)
    cv_email = models.EmailField(verbose_name = 'Custom Venue Email')
    cv_site = models.URLField(verbose_name = 'Custom Venue Website Address')
    cv_fcb = models.URLField(verbose_name = 'Custom Venue Facebook page')
    cv_twt = models.URLField(verbose_name = 'Custom Venue Twitter page')
    created_at = models.DateTimeField(verbose_name = 'Date created', auto_now_add = True)
    updated_at = models.DateTimeField(verbose_name = 'Date updated', auto_now = True)
    cv_user = models.ManyToManyField(Account, verbose_name = 'User profile')
    cv_about = models.TextField(verbose_name = 'Text for "About Us" block', default = 'Not provided')
    #cv_events = models.ManyToManyField(verbose_name = 'Events of given Venue Profile', null = True)
    cv_picture = ImageCropField(upload_to = 'venue_profile_imgs', blank=True, null=True, help_text='Custom Venue Profile picture')
    cv_cropping = ImageRatioField('cv_picture', '154x154', size_warning=True, allow_fullsize=True)
    cv_slug = models.SlugField(verbose_name = 'Unique URL for custom Venue, created from name', unique = True)
    
    
    class Meta:
        ordering = ['created_at']
        db_table = 'venue_profile'

