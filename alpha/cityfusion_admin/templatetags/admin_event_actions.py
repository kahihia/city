from django import template

register = template.Library()


@register.inclusion_tag('actions/report_event_popup.html', takes_context=True)
def report_event_popup(context, event):
    request = context['request']

    return {
        'account': request.account,
        'event': event
    }


@register.inclusion_tag('actions/claim_event_popup.html', takes_context=True)
def claim_event_popup(context, event):
    request = context['request']

    return {
        'account': request.account,
        'event': event
    }

@register.inclusion_tag('actions/actions.html', takes_context=True)
def admin_event_actions(context):
    return context


            
