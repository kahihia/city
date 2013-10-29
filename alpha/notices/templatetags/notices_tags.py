import json

from django import template
from django.template.loader import render_to_string

from ..models import Notice

register = template.Library()


@register.simple_tag(takes_context=True)
def notice_item(context, notice):
    params = json.loads(notice.log)
    params['notice_id'] = notice.id
    params['csrf_token'] = context['csrf_token']
    return render_to_string('notices/types/%s.html' % notice.type, params)


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