from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm

class CityRegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class']= 'text'
        self.fields['username'].label = _(u'Username')
        self.fields['email'].widget.attrs['class'] = 'text'
        self.fields['email'].label = _(u'Email')
        self.fields['password1'].widget.attrs['class'] = 'text password'
        self.fields['password1'].label = _(u'Password')
        self.fields['password2'].widget.attrs['class'] = 'text password'
        self.fields['password2'].label = _(u'Password (again)')

class CityAuthForm(AuthenticationForm):
    remember = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super(CityAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'text'
        self.fields['password'].widget.attrs['class'] = 'text password'
