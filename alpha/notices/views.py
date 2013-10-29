import json
from django.http import HttpResponse
from .models import Notice


def read_notice(request):
    notice_id = request.POST.get('notice_id', 0)

    try:
        notice = Notice.objects.get(pk=notice_id)
    except Notice.DoesNotExist:
        notice = None

    if notice:
        notice.read = True
        notice.save()

    return HttpResponse(json.dumps({'success': True}), mimetype='application/json')
