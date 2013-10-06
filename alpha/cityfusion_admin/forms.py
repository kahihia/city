from django import forms
from djmoney.forms.fields import MoneyField
from accounts.models import BonusCampaign


class FreeTryForm(forms.Form):
    bonus_budget = MoneyField()

class BonusCampaignForm(forms.ModelForm):
    budget = MoneyField()
    start_time = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'))
    end_time = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'))

    class Meta:
        model = BonusCampaign
        fields = (
            'start_time',
            'end_time',
            'budget',
            'apply_to_old_accounts'
        )
