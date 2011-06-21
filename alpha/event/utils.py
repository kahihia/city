import random
import string
from event.models import Event
from django import forms
from alpha.event.fields import JqSplitDateTimeField
from alpha.event.widgets import JqSplitDateTimeWidget

def get_event(auth_key):
    """
    Returns the event which matches the auth_key
    Throws ObjectDoesNotExist if not found
    """
    return Event.events.get(authentication_key__exact=auth_key)

def generate_form(*args):
    class HTML5DateTimeInput(forms.DateTimeInput):
        input_type = 'datetime'
    class HTML5EmailInput(forms.TextInput):
        input_type = 'email'

    """
    Generates an event form
    """
    class _EventForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_EventForm, self).__init__(*args,**kwargs)
            #self.fields['start_time'].widget = HTML5DateTimeInput(attrs={'class':'date_time'})
            self.fields['email'].widget = HTML5EmailInput()
        class Meta:
            model = Event
            exclude = tuple(args)
        start_time = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class':'datepicker','time_class':'timepicker'}))
    return _EventForm
