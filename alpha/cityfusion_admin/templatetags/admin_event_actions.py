from django import template


from accounts.models import Account
from django.shortcuts import get_object_or_404


register = template.Library()


@register.inclusion_tag('actions/report_event_popup.html', takes_context=True)
def report_event_popup(context, event):
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


@register.inclusion_tag('actions/claim_event_popup.html', takes_context=True)
def claim_event_popup(context, event):
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

@register.inclusion_tag('actions/actions.html', takes_context=True)
def admin_event_actions(context):
    return context


            
