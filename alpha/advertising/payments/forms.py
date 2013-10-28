from django import forms
from advertising.forms import AdvertisingSetupForm
from djmoney.forms.fields import MoneyField
from moneyed import Money, CAD


class BaseFundForm(forms.Form):
    order_budget = MoneyField(required=False)
    bonus_budget = MoneyField(required=False)

    def __init__(self, account, *args, **kwargs):
        super(BaseFundForm, self).__init__(*args, **kwargs)
        self.account = account


class BaseSetupForm(AdvertisingSetupForm):
    order_budget = MoneyField(required=False)
    bonus_budget = MoneyField(required=False)


class PaidFundForm(BaseFundForm):
    order_budget = MoneyField(min_value=Money(10, CAD))
    bonus_budget = MoneyField(required=False)

    def __init__(self, *args, **kwargs):
        super(PaidFundForm, self).__init__(*args, **kwargs)

        self.fields['order_budget'].error_messages['min_value'] = 'Ensure budget is greater than or equal to %(limit_value)s'


class PaidSetupForm(AdvertisingSetupForm):
    order_budget = MoneyField(min_value=Money(10, CAD))
    bonus_budget = MoneyField(required=False)

    def __init__(self, *args, **kwargs):
        super(PaidSetupForm, self).__init__(*args, **kwargs)

        self.fields['order_budget'].error_messages['min_value'] = 'Ensure budget is greater than or equal to %(limit_value)s'


class BonusPaymentsMixin(object):
    def clean(self):
        cleaned_data = super(BonusPaymentsMixin, self).clean()

        bonus_budget = cleaned_data["bonus_budget"]

        if bonus_budget > self.account.bonus_budget:
            raise forms.ValidationError('Ensure budget is lower than or equal to %s' % self.account.bonus_budget)

        return cleaned_data


    def save(self, commit=True):
        campaign = super(BonusPaymentsMixin, self).save(commit=False)

        cleaned_data = self.clean()

        campaign.budget = cleaned_data["bonus_budget"]

        if commit:
            campaign.save()

        return campaign


class BonusFundForm(forms.Form, BonusPaymentsMixin):
    order_budget = MoneyField(required=False)
    bonus_budget = MoneyField(min_value=Money(10, CAD))

    def __init__(self, account, *args, **kwargs):        
        super(BonusFundForm, self).__init__(*args, **kwargs)

        self.account = account

        self.fields['bonus_budget'].error_messages['min_value'] = 'Ensure budget is greater than or equal to %(limit_value)s'


class BonusSetupForm(AdvertisingSetupForm, BonusPaymentsMixin):
    order_budget = MoneyField(required=False)
    bonus_budget = MoneyField(min_value=Money(10, CAD))


SETUP_FORMS = {
    "paypal": PaidSetupForm,
    "bonus": BonusSetupForm
}

FUND_FORMS = {
    "paypal": PaidFundForm,
    "bonus": BonusFundForm
}


def setup_form(name):
    return SETUP_FORMS[name]

def fund_form(name):
    return FUND_FORMS[name]