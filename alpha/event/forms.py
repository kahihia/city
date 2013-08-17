from django import forms
from django.forms.widgets import RadioSelect
from event.models import Event, FeaturedEvent
from event.widgets import WhenWidget, PriceWidget, GeoCompleteWidget, WheelchairWidget, AjaxCropWidget, ChooseUserContextWidget
from django.utils.translation import ugettext_lazy as _
import string
from lookups import CityLookup
import selectable.forms as selectable
from gmapi.forms.widgets import LocationWidget
import json
from ckeditor.fields import RichTextFormField


class SetupFeaturedForm(forms.ModelForm):
    class Meta:
        model = FeaturedEvent
        fields = (
            'start_time',
            'end_time'
        )


class JSONCharField(forms.CharField):
    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, basestring):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                pass
        return value


YES_OR_NO = (
    (True, 'Yes'),
    (False, 'No')
)


class HTML5EmailInput(forms.TextInput):
    input_type = 'email'


class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('owner', 'authentication_key', 'slug', 'email')


    place = JSONCharField(
        widget=GeoCompleteWidget(),
        required=False
    )
    location = forms.Field(widget=LocationWidget(), required=False)
    venue_identifier = forms.CharField(required=False, widget=forms.widgets.HiddenInput())
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
    description = RichTextFormField(
        required=False
    )
    description_json = forms.CharField(
        required=True,
        widget=forms.widgets.HiddenInput()
    )

    price = forms.CharField(
        widget=PriceWidget(),
        required=False,
        initial="$"
    )

    wheelchair = forms.BooleanField(
        widget=WheelchairWidget(choices=YES_OR_NO),
        required=False
    )

    post_to_facebook = forms.BooleanField(
        widget=RadioSelect(choices=YES_OR_NO),
        required=False,
    )

    picture_src = forms.CharField(
        widget=AjaxCropWidget(),
        required=False
    )

    website = forms.URLField(required=False)
    tickets = forms.CharField(required=False)
    comment_for_facebook = forms.CharField(required=False)

    def __init__(self, account, *args, **kwargs):
        self.city_required = False
        super(EditEventForm, self).__init__(*args, **kwargs)

        self.fields['venue_account_owner'].widget = ChooseUserContextWidget(account)

        if 'email' in self.fields:
            self.fields['email'].widget = HTML5EmailInput(attrs={'class': 'text wide'})
            self.fields['email'].label = _(u'Email Address')

        self.fields['name'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['name'].widget.attrs['tabindex'] = 1
        self.fields['name'].error_messages['required'] = 'Event name is required'
        self.fields['name'].label = _(u'Event Name')

        self.fields['place'].error_messages['required'] = 'Your event cannot miss a location'
        self.fields['place'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['place'].label = _(u'Location')
        self.fields['place'].widget.attrs['tabindex'] = 2

        # Suggest venue popup
        self.fields['venue_name'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['street'].widget.attrs['class'] = 'inputfield rborder'

        self.fields['city'].error_messages['required'] = 'Your event cannot miss a city'
        self.fields['city'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['city'].label = _(u'City')

        self.fields['when'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['when'].widget.attrs['readonly'] = True
        self.fields['when'].widget.attrs['placeholder'] = "Click to select"
        self.fields['when'].error_messages['required'] = 'Please choose at least one date'
        self.fields['when'].widget.attrs['tabindex'] = 3

        self.fields['when_json'].error_messages['required'] = 'Please choose at least one date'

        self.fields['price'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['price'].label = _(u'Price')
        self.fields['price'].widget.attrs['tabindex'] = 4

        self.fields['description'].widget = forms.widgets.Textarea(attrs={'class': 'textarea rborder', 'tabindex': 5})

        self.fields['website'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['website'].widget.attrs['tabindex'] = 6
        self.fields['website'].error_messages['invalid'] = 'Enter a valid website url'

        self.fields['wheelchair'].widget.attrs['tabindex'] = 6

        self.fields['comment_for_facebook'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['comment_for_facebook'].widget.attrs['tabindex'] = 10

        self.fields['tags'].error_messages['required'] = 'Please enter at least one tag'
        self.fields['tags'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['tags'].widget.attrs['tabindex'] = 11

        self.fields['tickets'].widget.attrs['class'] = 'inputfield rborder'
        self.fields['tickets'].widget.attrs['tabindex'] = 12


        self.fields['picture_src'].label = _(u'Image')

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'tags' in cleaned_data:
            cleaned_data['tags'] = map(string.capwords, cleaned_data['tags'])

        place = cleaned_data["place"]

        if not cleaned_data["venue_account_owner"]:
            if cleaned_data["venue_identifier"]:
                pass
            elif cleaned_data["venue_name"]:
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

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if len(tags) > 10:
            raise forms.ValidationError("It is not possible to create more than 10 tags for event, please leave the most important")
        return tags


class CreateEventForm(EditEventForm):
    class Meta:
        model = Event
        exclude = ('owner', 'authentication_key', 'slug', 'email')
