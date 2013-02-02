from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm

class CityRegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class']= 'inputfield rborder'
        self.fields['username'].widget.attrs['tabindex']= '1'
        self.fields['username'].label = _(u'Username')
        self.fields['email'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['email'].label = _(u'Email')
        self.fields['email'].widget.attrs['tabindex']= '1'
        self.fields['password1'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['password1'].widget.attrs['tabindex']= '1'
        self.fields['password1'].label = _(u'Password')
        self.fields['password2'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['password2'].widget.attrs['tabindex']= '1'
        self.fields['password2'].label = _(u'Password (again)')

class CityAuthForm(AuthenticationForm):
    remember = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super(CityAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['username'].widget.attrs['tabindex'] = '1'
        self.fields['password'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['password'].widget.attrs['tabindex'] = '2'
        self.fields['remember'].widget.attrs['tabindex'] = '3'
