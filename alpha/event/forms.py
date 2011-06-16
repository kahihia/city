from django import forms
from alpha.event import models

attrs_dictionary = { 'class': 'required' }

class EventForm(forms.ModelForm):
    """
    Form for creating a new event
    Validates the event is not already created
    """
    class Meta:
        model = models.Event
        exclude = ('public_key', 'authentication_key',)

    #email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
    #                         label=_(u'email address'))
