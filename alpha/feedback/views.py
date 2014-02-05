from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import mail_managers
from django.core.urlresolvers import reverse

from home.models import Page
from .forms import ContactForm
from .models import Feedback


def feedback(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = 'From: %(name)s <%(email)s>\n\n%(type)s\n\n%(comments)s' % form.cleaned_data
            mail_managers("Cityfusion.ca Feedback", message, fail_silently=True)
            feedback = Feedback(**form.cleaned_data)
            feedback.save()
            return HttpResponseRedirect( reverse('feedback_thanks') )
    else:
        form = ContactForm()

    try:
        page_info = Page.objects.get(alias='feedback')
    except Page.DoesNotExist:
        page_info = {}

    return render_to_response("feedback/contact.html",
                              {'form': form,
                               'page_info': page_info},
                              context_instance=RequestContext(request))

def feedback_thanks(request):
    return render_to_response("feedback/contact_thanks.html", {}, context_instance=RequestContext(request))
