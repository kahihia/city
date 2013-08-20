# Create your views here.
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext, TemplateDoesNotExist

def custom_404(request):
    return render(request,"404.html")

def redirect(request):
    return HttpResponseRedirect(reverse('home'))

# for facebook connect
def channelfile(request):
    return HttpResponse('''<script src="//connect.facebook.net/en_US/all.js"></script>''')


def page(request, alias):
    import socket
    raise Exception(socket.gethostname())
    try:
        return render_to_response('pages/%s.html' % alias, context_instance=RequestContext(request))
    except TemplateDoesNotExist:
        raise Http404
