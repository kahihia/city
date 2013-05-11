#!/usr/bin/env python
#-*-coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import VenueProfile
from accounts.models import Account
from django.shortcuts import get_object_or_404

@login_required
def prprofile(request, prof_slug):
    venues_profile = get_object_or_404(VenueProfile, cv_slug = prof_slug)
    return render_to_response('prprofile.html', {
                'venues_profile' : venues_profile,
        },context_instance=RequestContext(request))
    
    
