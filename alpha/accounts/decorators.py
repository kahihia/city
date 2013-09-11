from accounts.models import Account
from functools import wraps
from django.utils.decorators import available_attrs
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
from urlparse import urljoin
import re


REDIRECT_FIELD_NAME_ACCOUNT = "redirect_after_edit_account"

http_re = re.compile('^https?:')

def get_absolute_uri(request):
    location = request.get_full_path()
    if not http_re.match(location): 
        current_uri = '%s://%s%s' % (request.is_secure() and 'https' or 'http', request.get_host(), request.path)
        location = urljoin(current_uri, location)
    return location


def account_passes_test(test_func, redirect_field_name=REDIRECT_FIELD_NAME, why_message=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            account = Account.objects.get(user_id=request.user.id)
            if test_func(account):
                return view_func(request, *args, **kwargs)

            path = get_absolute_uri(request)

            return HttpResponseRedirect(reverse("user_profile_required", kwargs= {
                "username": account.user.username, 
                "success_url": path,
                "why_message": why_message 
            }))
        return _wrapped_view
    return decorator


def native_region_required(redirect_field_name=REDIRECT_FIELD_NAME_ACCOUNT, why_message=None):
    actual_decorator = account_passes_test(
        lambda account: bool(account.tax_origin_confirmed and (account.not_from_canada or account.native_region)),
        redirect_field_name=redirect_field_name,
        why_message=why_message
    )
    return actual_decorator


def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        data = json.dumps({ 'not_authenticated': True })
        return HttpResponse(data, mimetype='application/json')
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap


def user_passes_test_with_403(test_func, login_url=None):
    """
    Decorator for views that checks that the user passes the given test.
    
    Anonymous users will be redirected to login_url, while users that fail
    the test will be given a 403 error.
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL
    def _dec(view_func):
        def _checklogin(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            elif not request.user.is_authenticated():
                return HttpResponseRedirect('%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, request.get_full_path()))
            else:
                resp = render_to_response('403.html', context_instance=RequestContext(request))
                resp.status_code = 403
                return resp
        _checklogin.__doc__ = view_func.__doc__
        _checklogin.__dict__ = view_func.__dict__
        return _checklogin
    return _dec    