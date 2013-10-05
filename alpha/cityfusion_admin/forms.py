from django import forms
from djmoney.forms.fields import MoneyField
from accounts.models import BonusCampaign


class FreeTryForm(forms.Form):
    bonus_budget = MoneyField()

class BonusCampaignForm(forms.ModelForm):
    bonus_budget = MoneyField()
    start_time = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'))
    end_time = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'))

    class Meta:
        model = BonusCampaign
        fields = (
            'start_time',
            'end_time',
            'bonus_budget'
        )
