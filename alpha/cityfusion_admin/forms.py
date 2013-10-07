from django import forms
from djmoney.forms.fields import MoneyField
from accounts.models import BonusCampaign


class FreeTryForm(forms.Form):
    bonus_budget = MoneyField()

class BonusCampaignForm(forms.ModelForm):
    budget = MoneyField()
    start_time = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), required=False)
    end_time = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), required=False)

    class Meta:
        model = BonusCampaign
        fields = (
            'start_time',
            'end_time',
            'budget',
            'apply_to_old_accounts'
        )

    def clean(self):
        cleaned_data = self.cleaned_data

        start_time = cleaned_data["start_time"]
        end_time = cleaned_data["end_time"]
        apply_to_old_accounts = cleaned_data["apply_to_old_accounts"]

        if not apply_to_old_accounts and not (start_time and end_time):
            raise forms.ValidationError('Start time and end time required')

        return cleaned_data
