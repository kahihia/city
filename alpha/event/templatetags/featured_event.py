from django import template
register = template.Library()



@register.inclusion_tag('featured/featured_event.html')
def featured_event(event):
    # TODO: use image for email

    event.featuredevent_set.all()[0].view()

    return {
        'event': event
    }
