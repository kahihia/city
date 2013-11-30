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
    def process_bonus(self):
        bonus = Decimal(self.request.POST["bonus"])

        if bonus:
            BonusFeaturedEventTransaction.objects.create(
                featured_event=self.featured_event,
                budget=bonus,
                order=self.order
            )

            Account.objects.filter(user_id=self.request.user.id).update(bonus_budget=F("bonus_budget")-bonus)


    def process_order(self):
        cost = (self.featured_event.end_time - self.featured_event.start_time).days * Money(2, CAD)
        bonus = Money(Decimal(self.request.POST["bonus"]), CAD)
        cost = cost - bonus

        if cost.amount:
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

            self.redirect_to_paypal = True

        else:
            order = FeaturedEventOrder(
                cost=cost,
                total_price=cost,
                featured_event=self.featured_event,
                account=self.account,
                status="s"
            )
            order.save()
            FeaturedEvent.objects.filter(id=self.featured_event.id).update(active=True)

        self.order = order


    def process_setup(self):
        self.redirect_to_paypal = False
        self.process_order()
        self.process_bonus()


    def redirect_to_next_step(self):
        if self.redirect_to_paypal:
            return HttpResponseRedirect(reverse('setup_featured_payment', args=(str(self.order.id),)))
        else:
            return HttpResponseRedirect(reverse('userena_profile_detail', kwargs={'username': self.request.user.username}))



def process_setup_featured(account, event, request):
    processor = PaypalPaymentProcessor(account, event, request)

    processor.process_setup()
    return processor.redirect_to_next_step()
