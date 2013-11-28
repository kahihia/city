from django import forms
from accounts.models import Account

from widgets import InTheLoopTagAutoSuggest, CityAutoSuggest
from taggit.forms import TagField
from accounts.models import REMINDER_TYPES

from userena.forms import EditProfileForm

import selectable.forms as selectable
from accounts.lookups import RegionLookup
from cities.models import Region
from localflavor.ca.forms import CAPhoneNumberField


class ReminderSettingsForm(forms.ModelForm):
    reminder_with_website = forms.BooleanField(required=False, label="")
    reminder_with_email = forms.BooleanField(required=False, label="")
    reminder_with_sms = forms.BooleanField(required=False, label="")
    reminder_active_type = forms.ChoiceField(widget=forms.RadioSelect, choices=REMINDER_TYPES)
    reminder_phonenumber = CAPhoneNumberField(required=False)

    class Meta:
        model = Account
        fields = (
            'reminder_with_website',
            'reminder_with_email',
            'reminder_with_sms',
            'reminder_email',
            'reminder_phonenumber',
            'reminder_days_before_event',
            'reminder_hours_before_event',
            'reminder_on_week_day',
            'reminder_active_type'
        )

    def __init__(self, *args, **kwargs):
        super(ReminderSettingsForm, self).__init__(*args, **kwargs)

        self.fields['reminder_days_before_event'].widget.attrs['maxlength'] = 2
        self.fields['reminder_hours_before_event'].widget.attrs['maxlength'] = 2


class InTheLoopSettingsForm(forms.ModelForm):
    in_the_loop_tags = TagField(widget=InTheLoopTagAutoSuggest())
    in_the_loop_with_website = forms.BooleanField(required=False, label="")
    in_the_loop_with_email = forms.BooleanField(required=False, label="")
    in_the_loop_with_sms = forms.BooleanField(required=False, label="")
    in_the_loop_phonenumber = CAPhoneNumberField(required=False)

    regions = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Region.objects.filter(country__code="CA"),
        required=False
    )

    cities = TagField(
        widget=CityAutoSuggest(),
        required=False
    )

    class Meta:
        model = Account
        fields = (
            'in_the_loop_tags',
            'in_the_loop_with_website',
            'in_the_loop_with_email',
            'in_the_loop_with_sms',
            'in_the_loop_email',
            'in_the_loop_phonenumber',
            'regions',
            'cities',
            'all_of_canada'
        )


class AccountForm(EditProfileForm):
    native_region = selectable.AutoCompleteSelectField(
        lookup_class=RegionLookup,
        required=False,
        widget=selectable.AutoComboboxSelectWidget(lookup_class=RegionLookup)
    )    

    class Meta:
        model = Account
        fields = [
            'mugshot',
            'date_of_birth',
            'native_region',
            'tax_origin_confirmed',
            'not_from_canada',
        ]
