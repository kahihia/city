from event.models import SingleEvent
from taggit.models import TaggedItem
from django.db.models import Count

def user_location(request):
    return {
        "user_location": request.user_location
    }   
        

def top5_tags(request):
    events = SingleEvent.future_events.all()

    top5_tags = TaggedItem.objects.filter(object_id__in=events.values_list("event_id", flat=True)) \
        .values('tag', 'tag__name') \
        .annotate(count=Count('id')) \
        .order_by('-count')[0:5]

    return {
        "top5_tags": top5_tags
    }
