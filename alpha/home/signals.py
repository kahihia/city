from django.contrib.auth.signals import user_logged_in


def after_login(sender, user, request, **kwargs):
    if request.GET.get('facebook_login', False):
    	profile = user.get_profile()
    	if not profile.new_token_required:
        	user.get_profile().extend_access_token()

user_logged_in.connect(after_login)