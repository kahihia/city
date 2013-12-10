import json
import selectable.forms as selectable
from django import forms
from django.core import validators
from accounts.models import VenueAccount, VenueType, VenueAccountSocialLink
from event.widgets import AjaxCropWidget, GeoCompleteWidget
from event.forms import JSONCharField
from gmapi.forms.widgets import LocationWidget
from event.lookups import CityLookup
from ckeditor.fields import RichTextFormField
from localflavor.ca.forms import CAPhoneNumberField

from widgets import VenueTagAutoSuggest
from taggit.forms import TagField

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
    fax = CAPhoneNumberField(required=False)
    about = RichTextFormField(required=False)

    tags = TagField(widget=VenueTagAutoSuggest(), required=False)

    social_links = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )

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
            'types',
            'tags'
        )

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if len(tags) > 10:
            raise forms.ValidationError("I'm sorry, but 10 tags is the maximum amount per event.")
        return tags

    def clean_social_links(self):
        if not self.cleaned_data["social_links"]:
            return []

        social_links = json.loads(self.cleaned_data["social_links"])["social_links"]

        for social_link in social_links:
            if not social_link["title"]:
                raise forms.ValidationError("Title is required")
            if not social_link["url"]:
                raise forms.ValidationError("Url is required")

            validators.URLValidator(message="Enter a valid URL.")(social_link["url"])

        return social_links

    def save(self, *args, **kwargs):        
        venue_account = super(VenueAccountForm, self).save(*args, **kwargs)
        venue_account.venueaccountsociallink_set.all().delete()

        social_links = self.cleaned_data["social_links"]

        for social_link in social_links:
            VenueAccountSocialLink.objects.create(
                title=social_link["title"],
                link=social_link["url"],
                venue_account=venue_account
            )

        return venue_account


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
