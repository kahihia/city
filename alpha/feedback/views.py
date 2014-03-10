import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import mail_managers
from django.core.mail.message import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.conf import settings

from home.models import Page
from .forms import ContactForm
from .models import Feedback


def feedback(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            hostname = request.get_host()
            time = datetime.datetime.now()

            if settings.MANAGERS:
                subject = '%s / Feedback' % hostname
                message_data = form.cleaned_data.copy()
                message_data['time'] = time.strftime('%d-%m-%Y, %-1I:%M %p')
                message = '''From: %(name)s <%(email)s>\n\nType: %(type)s\n\nTime: %(time)s
                            \nText: %(comments)s''' % message_data
                mail = EmailMultiAlternatives('%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject),
                                              message, message_data['email'], [a[1] for a in settings.MANAGERS],
                                              headers = {'Reply-To': message_data['email']})
                mail.send(fail_silently=True)

            feedback = Feedback(time=time, **form.cleaned_data)
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
