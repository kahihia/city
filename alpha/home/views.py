# Create your views here.
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext, TemplateDoesNotExist
from django.conf import settings
from django.contrib.sites.models import Site

from .services import sitemap_service

def custom_404(request):
    return render(request,"404.html")

def redirect(request):
    return HttpResponseRedirect(reverse('home'))

# for facebook connect
def channelfile(request):
    return HttpResponse('''<script src="//connect.facebook.net/en_US/all.js"></script>''')

def facebook_for_turbolinks_js(request):
    return render(request, 'facebook-for-turbolinks.js', {
            "FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID,
            "site": Site.objects.get_current().domain
        }, content_type="application/javascript")


def page(request, alias):
    try:
        return render_to_response('pages/%s.html' % alias, context_instance=RequestContext(request))
    except TemplateDoesNotExist:
        raise Http404

def sitemap(request):
    return HttpResponse(sitemap_service.get_sitemap_xml(), mimetype='text/xml')