from django import forms
from event.models import Event
from alpha.event.fields import JqSplitDateTimeField
from alpha.event.widgets import JqSplitDateTimeWidget
from django import forms
from django.utils.translation import ugettext_lazy as _                        

def generate_form(*args):
    class HTML5DateTimeInput(forms.DateTimeInput):
        input_type = 'datetime'
    class HTML5EmailInput(forms.TextInput):
        input_type = 'email'


    """
    Generates an event form
    """
    class _EventForm(forms.ModelForm):
        class Meta:
            model = Event
            exclude = tuple(args)
        def __init__(self, *args, **kwargs):
            super(_EventForm, self).__init__(*args,**kwargs)
            if 'email' in self.fields:
                self.fields['email'].widget = HTML5EmailInput(attrs={'class': 'text wide'})
            self.fields['name'].widget.attrs['class'] = 'text wide'
            self.fields['name'].label = _(u'Event Name')
            self.fields['location'].widget.attrs['class'] = 'text wide'
            self.fields['location'].label = _(u'Location')
            self.fields['start_time'].widget = forms.DateTimeInput(attrs={'class':'text wide date'})
            self.fields['end_time'].widget = forms.DateTimeInput(attrs={'class':'text wide date'})
            self.fields['start_time'].label = _(u'When')
            self.fields['description'].widget = forms.widgets.Textarea( attrs={ 'class':'wide', 
                                                                                'rows':5 } )
            self.fields['tags'].widget.attrs['class'] = 'text wide'
            self.fields['picture'].label = _(u'Image')


    return _EventForm
