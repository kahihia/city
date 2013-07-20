from django import template


from accounts.models import Account
from django.shortcuts import get_object_or_404


register = template.Library()


@register.inclusion_tag('events/actions/remind_me_popup.html', takes_context=True)
def remind_me_popup(context, event):
    request = context['request']

    user = request.user

    if request.user.is_authenticated():
        account = get_object_or_404(Account, user=user)

        return {
            'account': account,
            'event': event
        }

    else:
        return {
            'account': None
        }


@register.inclusion_tag('events/actions/in_the_loop_popup.html', takes_context=True)
def in_the_loop_popup(context, event):
    request = context['request']

    user = request.user

    if request.user.is_authenticated():
        account = get_object_or_404(Account, user=user)

        return {
            'account': account,
            'event': event,
            'request': request
        }

    else:
        return {
            'account': None
        }


@register.inclusion_tag('events/actions/buy_tickets_popup.html', takes_context=True)
def buy_tickets_popup(context, event):
    request = context['request']

    user = request.user

    if request.user.is_authenticated():
        account = get_object_or_404(Account, user=user)

        return {
            'account': account,
            'event': event
        }

    else:
        return {
            'account': None
        }        

@register.simple_tag(takes_context=True)
def uniq_id_for_in_the_loop_tags(context, increment=False):
    request = context['request']

    id = request.session.get("uniq_id_for_in_the_loop_tags", 1)
    if increment:
        request.session["uniq_id_for_in_the_loop_tags"] = id + 1
    return id