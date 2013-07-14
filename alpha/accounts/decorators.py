from accounts.models import Account
from functools import wraps
from django.utils.decorators import available_attrs
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


REDIRECT_FIELD_NAME = "redirect_after_edit_account"


def account_passes_test(test_func, redirect_field_name=REDIRECT_FIELD_NAME, why_message=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            account = Account.objects.get(user_id=request.user.id)
            if test_func(account):
                return view_func(request, *args, **kwargs)

            path = request.build_absolute_uri()

            return HttpResponseRedirect(reverse("user_profile_required", kwargs= {
                "username": account.user.username, 
                "success_url": path,
                "why_message": why_message 
            }))
        return _wrapped_view
    return decorator


def native_region_required(redirect_field_name=REDIRECT_FIELD_NAME, why_message=None):
    actual_decorator = account_passes_test(
        lambda account: bool(account.not_from_canada or account.native_region),
        redirect_field_name=redirect_field_name,
        why_message=why_message
    )
    return actual_decorator