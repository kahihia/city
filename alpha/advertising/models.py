from django.contrib.gis.db import models
from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager
from cities.models import Region
from mamona import signals
from mamona.models import build_payment_model
from decimal import Decimal
from django.db.models import Q
from django.db.models import F


class AdvertisingType(models.Model):
    name = models.CharField(max_length=128)
    width = models.IntegerField()
    height = models.IntegerField()
    cpm_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    cpc_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    active = models.BooleanField(default=True)

    objects = money_manager(models.Manager())

    def __unicode__(self):
        return "%s(%d x %d)" % (self.name, self.width, self.height)


class AdminAdvertisingCampaignManager(models.Manager):
    def get_query_set(self):
        return super(AdminAdvertisingCampaignManager, self).get_query_set()


class AdvertisingCampaign(models.Model):
    name = models.CharField(max_length=128)
    account = models.ForeignKey('accounts.Account')
    venue_account = models.ForeignKey('accounts.VenueAccount', blank=True, null=True)
    all_of_canada = models.BooleanField()
    regions = models.ManyToManyField(Region)
    budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    ammount_spent = MoneyField(max_digits=18, decimal_places=10, default_currency='CAD')

    started = models.DateTimeField(auto_now=True, auto_now_add=True)
    ended = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    website = models.URLField()

    owned_by_admin = models.BooleanField(default=False)

    objects = money_manager(models.Manager())
    admin = AdminAdvertisingCampaignManager()

    def __unicode__(self):
        return self.name

    def ammount_remaining(self):
        return self.budget - self.ammount_spent

    def regions_representation(self):
        return ", ".join(self.regions.all().values_list("name", flat=True))


PAYMENT_TYPE = (
    ('CPM', 'CPM'),
    ('CPC', 'CPC'),
)

REVIEWED_STATUS = (
    ('PENDING', 'PENDING'),
    ('ACCEPTED', 'ACCEPTED'),
    ('DENIED', 'DENIED')
)


class ActiveAdvertisingManager(models.Manager):
    def get_query_set(self):
        return super(ActiveAdvertisingManager, self).get_query_set().filter(
            (Q(review_status="ACCEPTED") & Q(campaign__ammount_spent__gt=F("campaign__budget"))) | Q(campaign__owned_by_admin=True)
        )

class AdminAdvertisingManager(models.Manager):
    def get_query_set(self):
        return super(AdminAdvertisingManager, self).get_query_set().filter(campaign__owned_by_admin=True)


class PendingAdvertisingManager(models.Manager):
    def get_query_set(self):
        return super(PendingAdvertisingManager, self).get_query_set().filter(review_status="PENDING")        


class Advertising(models.Model):
    ad_type = models.ForeignKey(AdvertisingType)
    campaign = models.ForeignKey(AdvertisingCampaign)
    payment_type = models.CharField(max_length=3, choices=PAYMENT_TYPE)
    image = models.ImageField(upload_to="advertising")
    reviewed = models.BooleanField(default=False)
    review_status = models.CharField(max_length=10, choices=REVIEWED_STATUS, default="PENDING")
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    # Copy when create campaign. We should not change price after creating
    cpm_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    cpc_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    objects = models.Manager()
    active = ActiveAdvertisingManager()
    admin = AdminAdvertisingManager()
    pending = PendingAdvertisingManager()

    def __unicode__(self):
        return "%s - %s: %d/%d" % (self.campaign, self.ad_type, self.views, self.clicks)

    def click(self):        
        self.clicks = self.clicks + 1
        
        if self.payment_type == "CPC":
            self.campaign.ammount_spent = self.campaign.ammount_spent + self.cpc_price
            self.campaign.save()
        self.save()

    def view(self):
        self.views = self.views + 1

        if self.payment_type == "CPM":
            self.campaign.ammount_spent = self.campaign.ammount_spent + (self.cpm_price/1000)
            self.campaign.save()

        self.save()

    def image_thumb(self):
        return u'<img src="%s" height="60" />' % self.image.url

    image_thumb.short_description = 'Image'
    image_thumb.allow_tags = True



class AdvertisingOrder(models.Model):
    budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    total_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD') # with taxes
    campaign = models.ForeignKey(AdvertisingCampaign)
    account = models.ForeignKey('accounts.Account')

    status = models.CharField(
            max_length=1,
            choices=(('s', 'success'), ('f', 'failure'), ('p', 'incomplete')),
            blank=True,
            default=''
    )

    def __unicode__(self):
        return "Order for %s" % self.campaign

AdvertisingPayment = build_payment_model(AdvertisingOrder, unique=True)

def get_items(self):
        """Retrieves item list using signal query. Listeners must fill
        'items' list with at least one item. Each item is expected to be
        a dictionary, containing at least 'name' element and optionally
        'unit_price' and 'quantity' elements. If not present, 'unit_price'
        and 'quantity' default to 0 and 1 respectively.

        Listener is responsible for providing item list with sum of prices
        consistient with Payment.amount. Otherwise the final amount may
        differ and lead to unpredictable results, depending on the backend used.
        """
        items = []
        signals.order_items_query.send(sender=type(self), instance=self, items=items)

        items.append({
            "unit_price": self.order.budget.amount,
            "name": "Advertising campaign %s" % self.order.campaign,
            "quantity": 1
        })

        for tax in self.order.account.taxes():
            items.append({
                "unit_price": (self.order.budget.amount * tax.tax).quantize(Decimal("0.01")),
                "name": tax.name,
                "quantity": 1
            })
        
        return items
AdvertisingPayment.get_items = get_items

import listeners
