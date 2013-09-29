from django.contrib.auth.signals import user_logged_in, user_logged_out
from django_facebook.utils import clear_persistent_graph_cache


def after_login(sender, user, request, **kwargs):
    if request.GET.get('facebook_login', False):
        profile = user.get_profile()
        if not profile.new_token_required and profile.access_token:
            user.get_profile().extend_access_token()

def after_logout(sender, user, request, **kwargs):
    clear_persistent_graph_cache(request)


user_logged_in.connect(after_login)
user_logged_out.connect(after_logout)