from django import forms
from event.models import Event
from event.widgets import WhenWidget, PriceWidget, GeoCompleteWidget, WheelchairWidget, DescriptionWidget, AjaxCropWidget
from django.utils.translation import ugettext_lazy as _
import string
from lookups import CityLookup
import selectable.forms as selectable
from gmapi.forms.widgets import LocationWidget


class reminderForm(forms.Form):
    event = forms.CharField(label='', max_length=100, required=False)
    email = forms.EmailField(label='')
    date = forms.DateTimeField(label='', required=False)

    def __init__(self, *args, **kwargs):
        super(reminderForm, self).__init__(*args, **kwargs)
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


class JSONCharField(forms.CharField):
    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, basestring):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                pass
        return value


def generate_form(*args):
    class HTML5DateTimeInput(forms.DateTimeInput):
        input_type = 'datetime'

    class HTML5EmailInput(forms.TextInput):
        input_type = 'email'
    """
    Generates an event form
    """
    YES_OR_NO = (
        (True, 'Yes'),
        (False, 'No')
    )

    class _EventForm(forms.ModelForm):
        place = JSONCharField(
            widget=GeoCompleteWidget(),
            required=False
        )
        location = forms.Field(widget=LocationWidget(), required=False)
        venue_name = forms.CharField(required=False)
        street = forms.CharField(required=False)
        city = forms.CharField(
            widget=selectable.AutoCompleteSelectWidget(CityLookup, allow_new=True),
            required=False
        )
        city_identifier = forms.CharField(required=False, widget=forms.widgets.HiddenInput())

        when = forms.CharField(
            widget=WhenWidget(),
            required=True
        )
        when_json = forms.CharField(
            required=True,
            widget=forms.widgets.HiddenInput()
        )
        description = forms.CharField(
            widget=DescriptionWidget(),
            required=False
        )
        description_json = forms.CharField(
            required=True,
            widget=forms.widgets.HiddenInput()
        )

        price = forms.CharField(
            widget=PriceWidget(),
            required=False
        )

        wheelchair = forms.BooleanField(
            widget=WheelchairWidget(choices=YES_OR_NO),
            required=False
        )
        picture_src = forms.CharField(
            widget=AjaxCropWidget(),
            required=False
        )

        website = forms.CharField(required=False)
        tickets = forms.CharField(required=False)

        class Meta:
            model = Event
            exclude = tuple(args)

        def __init__(self, *args, **kwargs):
            self.city_required = False
            super(_EventForm, self).__init__(*args, **kwargs)
            if 'email' in self.fields:
                self.fields['email'].widget = HTML5EmailInput(attrs={'class': 'text wide'})
                self.fields['email'].label = _(u'Email Address')

            self.fields['name'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['price'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['price'].label = _(u'Price')
            self.fields['price'].widget.attrs['placeholder'] = "xx.xx"
            self.fields['name'].error_messages['required'] = 'Event name is required'
            self.fields['name'].label = _(u'Event Name')

            self.fields['place'].error_messages['required'] = 'Your event cannot miss a location'
            self.fields['place'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['place'].label = _(u'Location')

            self.fields['venue_name'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['street'].widget.attrs['class'] = 'inputfield rborder'

            self.fields['city'].error_messages['required'] = 'Your event cannot miss a city'
            self.fields['city'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['city'].label = _(u'City')

            self.fields['when'].widget.attrs['class'] = 'inputfield rborder tcalInput'
            self.fields['when'].widget.attrs['readonly'] = True
            self.fields['when'].widget.attrs['placeholder'] = "Click to select"
            self.fields['when'].error_messages['required'] = 'Please choose at least one date'
            self.fields['when_json'].error_messages['required'] = 'Please choose at least one date'

            self.fields['description'].widget = forms.widgets.Textarea(attrs={'class': 'textarea rborder'})
            self.fields['tags'].error_messages['required'] = 'Please enter at least one tag'
            self.fields['tags'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['website'].widget.attrs['class'] = 'inputfield rborder'
            self.fields['tickets'].widget.attrs['class'] = 'inputfield rborder'

            self.fields['picture_src'].label = _(u'Image')

        def clean(self):
            cleaned_data = self.cleaned_data
            if 'tags' in cleaned_data:
                cleaned_data['tags'] = map(string.capwords, cleaned_data['tags'])

            place = cleaned_data["place"]

            if cleaned_data["venue_name"]:
                if not cleaned_data["city_identifier"]:
                    self.city_required = True
                    raise forms.ValidationError(u'City is required')
                if not cleaned_data["location"]:
                    raise forms.ValidationError(u'Location on the map is required')

            elif place["full"]:
                if not place["city"]:
                    raise forms.ValidationError(u'You need to select al least city')
                if not place["venue"] or \
                   not place["latitude"] or \
                   not place["longtitude"]:
                    raise forms.ValidationError(u'Invalid location')
            else:
                raise forms.ValidationError(u'Location is required')

            return cleaned_data
    return _EventForm
