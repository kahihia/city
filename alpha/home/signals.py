from django.contrib.auth.signals import user_logged_in


def after_login(sender, user, request, **kwargs):
    if user.get_profile().facebook_id:
        user.get_profile().extend_access_token()

user_logged_in.connect(after_login)