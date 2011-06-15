# Create your views here.
from django.shortcuts import render

def custom_404(request):
    return render(request,"404.html")

def home(request):
    return render(request, "home.html")
