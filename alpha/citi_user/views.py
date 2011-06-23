from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def terms(request):
    return render_to_response('registration/terms.html',
                              context_instance = RequestContext(request))
