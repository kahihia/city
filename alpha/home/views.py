# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect

def custom_404(request):
    return render(request,"404.html")

def home(request):
    return render(request, "home.html")

def redirect(request):
    return HttpResponseRedirect( reverse('home'))
