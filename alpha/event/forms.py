from django import forms
from event.models import Event, Reminder
from alpha.event.fields import JqSplitDateTimeField
from alpha.event.widgets import JqSplitDateTimeWidget, WhenWidget, PriceWidget
from django import forms
from django.utils.translation import ugettext_lazy as _
import string
from lookups import CityLookup
import selectable.forms as selectable
from gmapi import maps
from gmapi.forms.widgets import LocationWidget

class reminderForm(forms.Form):
    event = forms.CharField(label='', max_length=100, required=False)
    email = forms.EmailField(label='')
    date = forms.DateTimeField(label='', required=False)
    def __init__(self, *args, **kwargs):
        super(reminderForm, self).__init__(*args,**kwargs)
        self.fields['event'].widget.attrs['class'] = 'hide'
        self.fields['date'].widget.attrs['class'] = 'hide'
        self.fields['email'].widget.attrs['class'] = 'nice'
        #self.fields['name'].widget.attrs['value'] = {{'name'}}
        #self.fields['event'].widget.attrs['value'] = {{'event'}}

class StyledSplitDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None):
        if attrs:
            date_attrs = attrs.copy()
            time_attrs = attrs.copy()
        else:
            date_attrs = {}
            time_attrs = {}
        date_attrs['class'] = 'inputfield rborder tcal'
        time_attrs['class'] = 'inputfield rborder'
        widgets = (forms.DateInput(attrs=date_attrs, format=date_format),
                   forms.TimeInput(attrs=time_attrs, format=time_format))
        super(forms.SplitDateTimeWidget, self).__init__(widgets, attrs)

class StyledSplitDateTimeField(forms.SplitDateTimeField):
    widget = StyledSplitDateTimeWidget(time_format="%I:%M %p")

# gmap = maps.Map(opts = {
#     'center': maps.LatLng(-79.4163, -43.70011),
#     'mapTypeId': maps.MapTypeId.ROADMAP,
#     'zoom': 3,
#     'mapTypeControlOptions': {
#         'style': maps.MapTypeControlStyle.DROPDOWN_MENU
#     }
# })

def generate_form(*args):
    class HTML5DateTimeInput(forms.DateTimeInput):
        input_type = 'datetime'
    class HTML5EmailInput(forms.TextInput):
        input_type = 'email'
    """
    Generates an event form
    """
    class _EventForm(forms.ModelForm):
        location_name = forms.CharField(
            widget=selectable.AutoCompleteSelectWidget(CityLookup, allow_new=True),
            required=False
        )
        location = forms.Field(widget=LocationWidget())
        when = forms.CharField(
            widget= WhenWidget()
        )
        price = forms.CharField(
            widget=PriceWidget()
        )
        
        class Meta:
            model = Event
            exclude = tuple(args)
        def __init__(self, *args, **kwargs):
            super(_EventForm, self).__init__(*args,**kwargs)            
            if 'email' in self.fields:
                self.fields['email'].widget = HTML5EmailInput(attrs={'class': 'text wide'})
                self.fields['email'].label = _(u'Email Address')

            self.fields['name'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['price'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['price'].label = _(u'Price')
            self.fields['name'].error_messages['required'] = 'Event name is required'
            self.fields['name'].label = _(u'Event Name')
            self.fields['location_name'].error_messages['required'] = 'Your event cannot miss a location'
            self.fields['location_name'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['location_name'].label = _(u'Location')
            self.fields['location'].error_messages['required'] = 'Your event cannot miss a location'
            self.fields['when'].widget.attrs['class'] = 'inputfield rborder tcalInput'
            self.fields['when'].widget.attrs['readonly'] = True
            self.fields['when'].widget.attrs['placeholder'] = "Click to select"


            self.fields['description'].widget = forms.widgets.Textarea( attrs={ 'class':'textarea rborder'} )
            self.fields['tags'].error_messages['required'] = 'Please enter at least one tag'
            self.fields['tags'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['website'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['picture'].label = _(u'Image')
            self.fields['picture'].widget.attrs['class'] = 'inputfield rborder'
        def clean(self):
            cleaned_data= self.cleaned_data
            if 'tags' in cleaned_data:
                cleaned_data['tags'] = map(string.capwords,cleaned_data['tags'])
            return cleaned_data
    return _EventForm