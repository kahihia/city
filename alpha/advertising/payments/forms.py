from django import forms
from advertising.forms import AdvertisingSetupForm
from djmoney.forms.fields import MoneyField


class PaypalFundForm(forms.Form):
    order_budget = MoneyField(required=False)
    bonus_budget = MoneyField(required=False)

    def __init__(self, account, *args, **kwargs):
        super(PaypalFundForm, self).__init__(*args, **kwargs)
        self.account = account

    def clean(self):
        cleaned_data = super(PaypalFundForm, self).clean()

        order_budget = cleaned_data["order_budget"]
        bonus_budget = cleaned_data["bonus_budget"]

        if not order_budget.amount and not bonus_budget.amount:
            raise forms.ValidationError('You need to specify budget')

        if bonus_budget > self.account.bonus_budget:
            raise forms.ValidationError('Ensure budget is lower than or equal to %s' % self.account.bonus_budget)

        return cleaned_data


class PaypalSetupForm(AdvertisingSetupForm):
    order_budget = MoneyField(required=False)
    bonus_budget = MoneyField(required=False)

    def save(self, commit=True):
        campaign = super(PaypalSetupForm, self).save(commit=False)

        cleaned_data = self.clean()

        campaign.budget = cleaned_data["bonus_budget"]

        if commit:
            campaign.save()

        return campaign

