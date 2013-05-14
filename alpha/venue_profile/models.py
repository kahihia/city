#!/usr/bin/env python
#-*-coding: UTF-8-*-

from django.db import models

from event.models import Venue
from accounts.models import Account
from image_cropping import ImageCropField, ImageRatioField


class VenueProfile(Venue):
    phone = models.CharField(verbose_name='Custom Venue Phone', max_length=20)
    fax = models.CharField(verbose_name='Custom Venue Fax', max_length=20)
    email = models.EmailField(verbose_name='Custom Venue Email')
    site = models.URLField(verbose_name='Custom Venue Website Address')
    facebook = models.URLField(verbose_name='Custom Venue Facebook page')
    twitter = models.URLField(verbose_name='Custom Venue Twitter page')
    created_at = models.DateTimeField(verbose_name='Date created', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Date updated', auto_now=True)
    account = models.ManyToManyField(Account, verbose_name='User profile')
    about = models.TextField(verbose_name='Text for "About Us" block', default='Not provided')
    picture = ImageCropField(upload_to='venue_profile_imgs', blank=True, null=True, help_text='Custom Venue Profile picture')
    cropping = ImageRatioField('picture', '154x154', size_warning=True, allow_fullsize=True)
    slug = models.SlugField(verbose_name='Unique URL for custom Venue, created from name', unique=True)
