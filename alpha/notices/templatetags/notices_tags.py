import json

from django import template
from django.template.loader import render_to_string

from ..models import Notice

register = template.Library()


@register.simple_tag(takes_context=True)
def notice_item(context, notice, history=False):
    params = json.loads(notice.log)
    params['notice_id'] = notice.id
    params['csrf_token'] = context['csrf_token']
    params['read'] = notice.read

    template_name = notice.type + '_history' if history else notice.type
    return render_to_string('notices/types/%s.html' % template_name, params)


@register.simple_tag(takes_context=True)
def notices_block(context, user):
    notice_count = Notice.objects.filter(user=user, read=False).count()
    if notice_count:
        return render_to_string('notices/notices_block.html', {
            'user': user,
            'notice_count': notice_count,
            'STATIC_URL': context['STATIC_URL']
        })
    else:
        return ''