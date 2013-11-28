import selectable.forms as selectable
from django import forms
from accounts.models import VenueAccount, VenueType
from event.widgets import AjaxCropWidget, GeoCompleteWidget
from event.forms import JSONCharField
from gmapi.forms.widgets import LocationWidget
from event.lookups import CityLookup
from ckeditor.fields import RichTextFormField
from localflavor.ca.forms import CAPhoneNumberField

class VenueAccountForm(forms.ModelForm):
    picture_src = forms.CharField(
        widget=AjaxCropWidget(),
        required=False
    )

    types = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=VenueType.active_types.all(),
        required=False
    )

    phone = CAPhoneNumberField(required=False)
    about = RichTextFormField(required=False)

    class Meta:
        model = VenueAccount

        fields = (
            'phone',
            'fax',
            'email',
            'site',
            'facebook',
            'myspace',
            'twitter',
            'about',
            'cropping',
            'types'
        )


class NewVenueAccountForm(VenueAccountForm):
    place = JSONCharField(
        widget=GeoCompleteWidget(),
        required=False
    )

    location = forms.Field(widget=LocationWidget(), required=False)
    venue_identifier = forms.CharField(required=False, widget=forms.widgets.HiddenInput())
    venue_name = forms.CharField(required=False)
    street = forms.CharField(required=False)
    street_number = forms.CharField(required=False)
    city = forms.CharField(
        widget=selectable.AutoCompleteSelectWidget(CityLookup, allow_new=True),
        required=False
    )
    city_identifier = forms.CharField(required=False, widget=forms.widgets.HiddenInput())
    about = RichTextFormField(required=False)

    def clean(self):
        cleaned_data = self.cleaned_data

        place = cleaned_data["place"]

        if not cleaned_data["venue_identifier"] and\
            (not place["venue"] or \
            not place["latitude"] or \
            not place["longtitude"]):
            raise forms.ValidationError(u'You should choose venue from list')

        return cleaned_data