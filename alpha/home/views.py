# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

def custom_404(request):
    return render(request,"404.html")

def home(request):
    return render(request, "home.html")

def redirect(request):
    return HttpResponseRedirect( reverse('home'))

# for facebook connect
def channelfile(request):
    return HttpResponse('''<script src="//connect.facebook.net/en_US/all.js"></script>''')
