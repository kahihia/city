from django import forms
from event.models import Event
from alpha.event.fields import JqSplitDateTimeField
from alpha.event.widgets import JqSplitDateTimeWidget
from django import forms

class HTML5DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime'

class HTML5EmailInput(forms.TextInput):
    input_type = 'email'

class EventFormLoggedIn(forms.ModelForm):
    """
    Form for creating a new event
    Used if user is logged in already
    """
    class Meta:
        model = Event
        exclude = ('owner', 'authentication_key', 'slug', 'email')

    def __init__(self, *args, **kwargs):
        super(EventFormLoggedIn, self).__init__(*args,**kwargs)
        #self.fields['start_time'].widget = HTML5DateTimeInput(attrs={'class':'date_time'})

    start_time = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs=  {'date_class':'datepicker','time_class':'timepicker'}))

class EventForm(forms.ModelForm):
    """
    Form for creating a new event
    Validates the event is not already created
    """
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args,**kwargs)
        #self.fields['start_time'].widget = HTML5DateTimeInput(attrs={'class':'date_time'})
        self.fields['email'].widget = HTML5EmailInput()

    class Meta:
        model = Event
        exclude = ('owner', 'authentication_key', 'slug')

    start_time = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs= {'date_class':'datepicker','time_class':'timepicker'}))
