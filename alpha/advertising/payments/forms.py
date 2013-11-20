from django import forms
from advertising.forms import AdvertisingSetupForm
from djmoney.forms.fields import MoneyField
from moneyed import Money, CAD


class PaypalFundForm(forms.Form):
    budget = MoneyField(required=False)
    bonus = MoneyField(required=False)

    def __init__(self, account, *args, **kwargs):
        super(PaypalFundForm, self).__init__(*args, **kwargs)
        self.account = account

        self.fields['budget'].error_messages['min_value'] = 'Ensure budget is greater than or equal to %(limit_value)s'

    def clean(self):
        cleaned_data = super(PaypalFundForm, self).clean()

        budget = cleaned_data["budget"]
        bonus = cleaned_data["bonus"]

        if budget.amount < 10:
            raise forms.ValidationError('Ensure budget is greater than or equal to %s' % Money(10, CAD))

        if bonus.amount > budget.amount:
            raise forms.ValidationError('Ensure budget is greater than bonus')

        if bonus > self.account.bonus_budget:
            raise forms.ValidationError('Ensure bonus is lower than or equal to %s' % self.account.bonus_budget)

        return cleaned_data


class PaypalSetupForm(AdvertisingSetupForm):
    budget = MoneyField(min_value=Money(10, CAD))
    bonus = MoneyField(required=False)

    def clean(self):
        cleaned_data = super(PaypalSetupForm, self).clean()

        budget = cleaned_data["budget"]
        bonus = cleaned_data["bonus"]

        if bonus.amount > budget.amount:
            raise forms.ValidationError('Ensure budget is greater than bonus')

        if bonus > self.account.bonus_budget:
            raise forms.ValidationError('Ensure bonus is lower than or equal to %s' % self.account.bonus_budget)

        return cleaned_data
