from django.db.models import F
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from advertising.models import AdvertisingOrder, AdvertisingCampaign, BonusAdvertisingTransaction
from accounts.models import Account, AccountTaxCost
from decimal import Decimal


class BasePaymentProcessor(object):
    def __init__(self, account, campaign, request):
        self.account = account
        self.campaign = campaign
        self.request = request

    def process_setup(self):
        raise NotImplementedError

    def process_fund(self):
        raise NotImplementedError        

    def redirect_to_next_step(self):
        raise NotImplementedError


class PaypalPaymentProcessor(BasePaymentProcessor):
    def process_setup(self):
        order_budget = Decimal(self.request.POST["order_budget"])
        total_price = order_budget

        for tax in self.account.taxes():
            total_price = total_price + (order_budget * tax.tax)

        order = AdvertisingOrder(
            budget=order_budget,
            total_price=total_price,
            campaign=self.campaign,
            account=self.account
        )

        order.save()

        for tax in self.account.taxes():
            account_tax_cost = AccountTaxCost(account_tax=tax, cost=order_budget*tax.tax, tax_name=tax.name)
            account_tax_cost.save()
            order.taxes.add(account_tax_cost)

        self.order = order

    def process_fund(self):
        self.process_setup()

    def redirect_to_next_step(self):
        return HttpResponseRedirect(reverse('advertising_payment', args=(str(self.order.id), )))     


class BonusPaymentProcessor(BasePaymentProcessor):
    def process_setup(self):
        budget = Decimal(self.request.POST["bonus_budget"])
        BonusAdvertisingTransaction.objects.create(
            campaign=self.campaign,
            budget=budget
        )

        Account.objects.filter(user_id=self.request.user.id).update(bonus_budget=F("bonus_budget")-budget)
        AdvertisingCampaign.objects.filter(id=self.campaign.id).update(budget=F("budget")+budget)

    def process_fund(self):
        self.process_setup()

    def redirect_to_next_step(self):
        return HttpResponseRedirect(reverse('advertising_deposit_funds_for_campaign', args=(self.campaign.id, )))


PAYMENT_PROCESSORS = {
    "paypal": PaypalPaymentProcessor,
    "bonus": BonusPaymentProcessor
}


def process_setup_campaign(payment_module, account, campaign, request):
    processor = PAYMENT_PROCESSORS[payment_module](account, campaign, request)

    processor.process_setup()
    return processor.redirect_to_next_step()

def process_fund_campaign(payment_module, account, campaign, request):
    processor = PAYMENT_PROCESSORS[payment_module](account, campaign, request)

    processor.process_fund()
    return processor.redirect_to_next_step()    
