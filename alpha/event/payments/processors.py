from django.db.models import F
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from event.models import FeaturedEventOrder, FeaturedEvent, BonusFeaturedEventTransaction
from accounts.models import Account, AccountTaxCost
from moneyed import Money, CAD
from decimal import Decimal


class BasePaymentProcessor(object):
    def __init__(self, account, featured_event, request):
        self.account = account
        self.featured_event = featured_event        
        self.request = request

    def process_setup(self):
        raise NotImplementedError    

    def redirect_to_next_step(self):
        raise NotImplementedError


class PaypalPaymentProcessor(BasePaymentProcessor):
    def process_setup(self):
        cost = (self.featured_event.end_time - self.featured_event.start_time).days * Money(2, CAD)
        bonus = Money(Decimal(self.request.POST["bonus"]), CAD)
        cost = cost - bonus

        total_price = cost

        for tax in self.account.taxes():
            total_price = total_price + (cost * tax.tax)

        order = FeaturedEventOrder(
            cost=cost,
            total_price=total_price,
            featured_event=self.featured_event,
            account=self.account
        )

        order.save()

        for tax in self.account.taxes():
            account_tax_cost = AccountTaxCost(account_tax=tax, cost=cost*tax.tax, tax_name=tax.name)
            account_tax_cost.save()
            order.taxes.add(account_tax_cost)

        self.order = order


    def redirect_to_next_step(self):
        return HttpResponseRedirect(reverse('setup_featured_payment', args=(str(self.order.id),)))


class BonusPaymentProcessor(BasePaymentProcessor):
    def process_setup(self):        
        budget = (self.featured_event.end_time - self.featured_event.start_time).days * Money(2, CAD)

        BonusFeaturedEventTransaction.objects.create(
            featured_event=self.featured_event,
            budget=budget
        )

        FeaturedEvent.objects.filter(id=self.featured_event.id).update(active=True)
        Account.objects.filter(user_id=self.request.user.id).update(bonus_budget=F("bonus_budget")-budget.amount)


    def redirect_to_next_step(self):
        return HttpResponseRedirect('/accounts/%s/' % self.request.user.username)


PAYMENT_PROCESSORS = {
    "paypal": PaypalPaymentProcessor,
    "bonus": BonusPaymentProcessor
}


def process_setup_featured(payment_module, account, event, request):
    processor = PAYMENT_PROCESSORS[payment_module](account, event, request)

    processor.process_setup()
    return processor.redirect_to_next_step()
