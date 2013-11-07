from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.inclusion_tag('events/actions/remind_me_popup.html', takes_context=True)
def remind_me_popup(context, event):
    request = context['request']

    return {
        'account': request.account,
        'event': event
    }


@register.inclusion_tag('events/actions/in_the_loop_popup.html', takes_context=True)
def in_the_loop_popup(context, event):
    request = context['request']    

    return {
        'account': request.account,
        'event': event,
        'request': request
    }




@register.inclusion_tag('events/actions/buy_tickets_popup.html', takes_context=True)
def buy_tickets_popup(context, event):
    request = context['request']

    return {
        'account': request.account,
        'event': event
    }

@register.simple_tag(takes_context=True)
def uniq_id_for_in_the_loop_tags(context, increment=False):
    request = context['request']

    id = request.session.get("uniq_id_for_in_the_loop_tags", 1)
    if increment:
        request.session["uniq_id_for_in_the_loop_tags"] = id + 1
    return id


@register.inclusion_tag('events/list/event_block.html', takes_context=True)
def event_block(context, event):
    STATIC_URL = context['STATIC_URL']
    return {
        'event': event,
        'STATIC_URL': STATIC_URL
    }


@register.inclusion_tag('events/list/short_single_event.html', takes_context=True)
def short_single_event(context, event):
    STATIC_URL = context['STATIC_URL']
    return {
        'event': event,
        'STATIC_URL': STATIC_URL
    }


@register.inclusion_tag('events/actions/auth_required_popup.html', takes_context=True)    
def auth_required_popup(context):
    request = context['request']
    return {
        "account": request.account
    }


@register.simple_tag(takes_context=True)
def event_link(context, event):
    return render_to_string('events/list/event_link.html', {'event': event}).strip()