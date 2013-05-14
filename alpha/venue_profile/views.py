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
def private_profile(request, slug):
    # user = request.user
    # account = get_object_or_404(Account, user=user)

    venue_profile = VenueProfile.objects.get(slug=slug)

    return render_to_response('private_profile.html', {
                'venue_profile': venue_profile,
        }, context_instance=RequestContext(request))


def public_profile(request, slug):
    venue_profile = VenueProfile.objects.get(slug=slug)

    return render_to_response('public_profile.html', {
                'venue_profile': venue_profile,
        }, context_instance=RequestContext(request))
