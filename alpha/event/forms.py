from django import forms
from event.models import Event
from alpha.event.fields import JqSplitDateTimeField
from alpha.event.widgets import JqSplitDateTimeWidget
from django import forms
from django.utils.translation import ugettext_lazy as _                        
import string

class StyledSplitDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None):
        if attrs:
            date_attrs = attrs.copy()
            time_attrs = attrs.copy()
        else:
            date_attrs = {}
            time_attrs = {}
        date_attrs['class'] = 'text wide date'
        time_attrs['class'] = 'text time'
        widgets = (forms.DateInput(attrs=date_attrs, format=date_format),
                   forms.TimeInput(attrs=time_attrs, format=time_format))
        super(forms.SplitDateTimeWidget, self).__init__(widgets, attrs)

class StyledSplitDateTimeField(forms.SplitDateTimeField):
    widget = StyledSplitDateTimeWidget(time_format="%I:%M %p")

def generate_form(*args):
    class HTML5DateTimeInput(forms.DateTimeInput):
        input_type = 'datetime'
    class HTML5EmailInput(forms.TextInput):
        input_type = 'email'
    """
    Generates an event form
    """
    class _EventForm(forms.ModelForm):
        recurrence = forms.BooleanField()
        start_time = StyledSplitDateTimeField(input_time_formats=['%I:%M %p'], label=_(u'Start Time'))
        end_time = StyledSplitDateTimeField(required = False, input_time_formats=['%I:%M %p'], label=_(u'End Time'))
        class Meta:
            model = Event
            exclude = tuple(args)
        def __init__(self, *args, **kwargs):
            super(_EventForm, self).__init__(*args,**kwargs)
            if 'email' in self.fields:
                self.fields['email'].widget = HTML5EmailInput(attrs={'class': 'text wide'})
                self.fields['email'].label = _(u'Email Address')
            self.fields['name'].widget.attrs['class'] = 'text wide'
            self.fields['price'].widget.attrs['class'] = 'text wide'
            self.fields['price'].label = _(u'Price')
            self.fields['name'].label = _(u'Event Name')
            self.fields['location'].widget.attrs['class'] = 'text wide'
            self.fields['location'].label = _(u'Location')
            self.fields['description'].widget = forms.widgets.Textarea( attrs={ 'class':'wide', 'rows':5 } )
            self.fields['tags'].widget.attrs['class'] = 'text wide'
            self.fields['website'].widget.attrs['class'] = 'text wide'
            self.fields['picture'].label = _(u'Image')
            self.fields['picture'].widget.attrs['class'] = 'file' 
        def clean(self):
            cleaned_data= self.cleaned_data
            if 'tags' in cleaned_data:
                cleaned_data['tags'] = map(string.capwords,cleaned_data['tags'])
            return cleaned_data
    return _EventForm
