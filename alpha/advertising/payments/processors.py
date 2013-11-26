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
    def process_bonus(self):
        bonus = Decimal(self.request.POST["bonus"])

        if bonus:
            BonusAdvertisingTransaction.objects.create(
                campaign=self.campaign,
                budget=bonus,
                order=self.order
            )

            Account.objects.filter(user_id=self.request.user.id).update(bonus_budget=F("bonus_budget")-bonus)
            AdvertisingCampaign.objects.filter(id=self.campaign.id).update(
                budget=F("budget")+bonus,
                enough_money=True
            )

    def process_order(self):
        order_budget = Decimal(self.request.POST["budget"]) - Decimal(self.request.POST["bonus"])

        if order_budget:
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

            self.redirect_to_paypal = True

        else:
            order = AdvertisingOrder(
                budget=order_budget,
                total_price=order_budget,
                campaign=self.campaign,
                account=self.account,
                status="s"
            )

            order.save()

        self.order = order

    def process(self):
        self.redirect_to_paypal = False
        self.process_order()
        self.process_bonus()
        

    def redirect_to_next_step(self):
        if self.redirect_to_paypal:
            return HttpResponseRedirect(reverse('advertising_payment', args=(str(self.order.id), )))     
        else:
            return HttpResponseRedirect(reverse('advertising_deposit_funds_for_campaign', args=(self.campaign.id, )))


def process_payment_for_campaign(account, campaign, request):
    processor = PaypalPaymentProcessor(account, campaign, request)

    processor.process()
    return processor.redirect_to_next_step()    
