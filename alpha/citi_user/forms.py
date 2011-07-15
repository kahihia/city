from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _


class CityAuthForm(AuthenticationForm):
    remember = forms.BooleanField(label=_"Remember me", required=False)
