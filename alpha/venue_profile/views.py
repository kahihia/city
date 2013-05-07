#!/usr/bin/env python
#-*-coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import VenueProfile

@login_required
def prprofile(request):
    user = request.user
    venues_profile = user.venueprofile_set.all()[0]
    return render_to_response('prprofile.html', {
                'venues_profile' : venues_profile,
        },context_instance=RequestContext(request),)
    
