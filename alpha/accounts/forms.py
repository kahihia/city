from django import forms
from accounts.models import Account, VenueAccount, VenueType

from django.utils.html import format_html

from widgets import InTheLoopTagAutoSuggest
from taggit.forms import TagField
from accounts.models import REMINDER_TYPES

from event.widgets import AjaxCropWidget
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text


class ReminderSettingsForm(forms.ModelForm):
    reminder_with_website = forms.BooleanField(required=False, label="")
    reminder_with_email = forms.BooleanField(required=False, label="")
    reminder_with_sms = forms.BooleanField(required=False, label="")
    reminder_active_type = forms.ChoiceField(widget=forms.RadioSelect, choices=REMINDER_TYPES)

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

    class Meta:
        model = Account
        fields = (
            'in_the_loop_tags',
            'in_the_loop_with_website',
            'in_the_loop_with_email',
            'in_the_loop_with_sms',
            'in_the_loop_email',
            'in_the_loop_phonenumber'
        )


class FusionCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    pass


class VenueAccountForm(forms.ModelForm):
    picture_src = forms.CharField(
        widget=AjaxCropWidget(),
        required=False
    )

    types = forms.ModelMultipleChoiceField(
        widget=FusionCheckboxSelectMultiple,
        queryset=VenueType.active_types.all(),
        required=False
    )

    class Meta:
        model = VenueAccount

        fields = (
            'phone',
            'fax',
            'email',
            'site',
            'facebook',
            'twitter',
            'about',
            'cropping',
            'types'
        )
