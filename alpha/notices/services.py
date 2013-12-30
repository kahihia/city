import json

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail.message import EmailMessage

from .models import Notice
from event.settings import DEFAULT_FROM_EMAIL


def create_notice(notice_type, user, mail_data={}, notice_data={}):
    log = json.dumps(notice_data)
    Notice.objects.create(type=notice_type, user=user, log=log)

    email = user.get_profile().reminder_email

    if email and mail_data:
        current_site = Site.objects.get_current().domain
        mail_data['site'] = current_site
        message = render_to_string('mail/%s.txt' % notice_type, mail_data)

        msg = EmailMessage(mail_data['subject'],
                           message,
                           DEFAULT_FROM_EMAIL,
                           [user.get_profile().reminder_email])
        msg.content_subtype = 'html'
        msg.send()