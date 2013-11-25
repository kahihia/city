import datetime
from moneyed import Money, CAD
from django.contrib.gis.db import models
from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager
from cities.models import Region
from mamona import signals
from mamona.models import build_payment_model
from decimal import Decimal
from django.db.models import Q, F
from utils import inform_user_that_money_was_spent

def has_changed(instance, field):
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.filter(pk=instance.pk).values(field).get()[field]

    return not getattr(instance, field) == old_value  


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
        return super(AdminAdvertisingCampaignManager, self).get_query_set().filter(
            Q(budget__gt=0) | Q(free=True)
        )

class AdvertisinCampaignWithUnsusedMoney(models.Manager):
    def get_query_set(self):
        return super(AdvertisinCampaignWithUnsusedMoney, self).get_query_set().filter(
            active_to__lt=datetime.datetime.now(),
            enough_money=True
        )


class AdvertisingCampaign(models.Model):
    name = models.CharField(max_length=128)
    account = models.ForeignKey('accounts.Account')
    venue_account = models.ForeignKey('accounts.VenueAccount', blank=True, null=True, on_delete=models.SET_NULL)
    all_of_canada = models.BooleanField()
    regions = models.ManyToManyField(Region)
    
    budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    ammount_spent = MoneyField(max_digits=18, decimal_places=10, default_currency='CAD')

    enough_money = models.BooleanField(default=False)

    started = models.DateTimeField(auto_now=True, auto_now_add=True)
    ended = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    active_from = models.DateTimeField('active to', null=True, blank=True, auto_now=False, auto_now_add=False)
    active_to = models.DateTimeField('active to', null=True, blank=True, auto_now=False, auto_now_add=False)

    website = models.URLField()

    free = models.BooleanField(default=False)

    objects = money_manager(models.Manager())
    admin = AdminAdvertisingCampaignManager()
    with_unused_money = AdvertisinCampaignWithUnsusedMoney()

    def save(self, *args, **kwargs):
        if self.ammount_spent >= self.budget:
            self.enough_money = False
        else:
            self.enough_money = True
        if has_changed(self, 'ammount_spent') and self.budget>Money(0, CAD):
            if self.ammount_spent >= self.budget:
                inform_user_that_money_was_spent(self)

        super(AdvertisingCampaign, self).save(*args, **kwargs)
        return self

    def __unicode__(self):
        return self.name

    def ammount_remaining(self):
        return self.budget - self.ammount_spent

    def regions_representation(self):
        return ", ".join(self.regions.all().values_list("name", flat=True))

    def is_active(self):
        now = datetime.datetime.now()
        return (self.enough_money or self.free) and (not self.active_from or self.active_from < now) and (not self.active_to or self.active_to > now)

    def is_finished(self):
        return self.active_to and self.active_to < datetime.datetime.now()

    def is_future(self):
        return self.active_from and self.active_from > datetime.datetime.now()


class ShareAdvertisingCampaign(models.Model):
    campaign = models.ForeignKey(AdvertisingCampaign)
    account = models.ForeignKey("accounts.Account")


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
        now = datetime.datetime.now()
        return super(ActiveAdvertisingManager, self).get_query_set().filter(
            ((Q(review_status="ACCEPTED") & Q(campaign__enough_money=True)) | Q(campaign__free=True)) & 
            (Q(campaign__active_to__isnull=True) | Q(campaign__active_to__gte=now)) &
            (Q(campaign__active_from__isnull=True) | Q(campaign__active_from__lte=now))
        ).select_related("campaign")


class FreeAdvertisingManager(models.Manager):
    def get_query_set(self):
        return super(FreeAdvertisingManager, self).get_query_set().filter(campaign__free=True)


class PendingAdvertisingManager(models.Manager):
    def get_query_set(self):
        return super(PendingAdvertisingManager, self).get_query_set().filter(
            review_status="PENDING",
            campaign__enough_money=True
        )


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
    free = FreeAdvertisingManager()
    pending = PendingAdvertisingManager()

    def __unicode__(self):
        return "%s - %s: %d/%d" % (self.campaign, self.ad_type, self.views, self.clicks)

    def click(self):
        Advertising.objects.filter(id=self.id).update(clicks=F("clicks")+1)
        
        if self.payment_type == "CPC":
            self.campaign.ammount_spent = self.campaign.ammount_spent + self.cpc_price
            self.campaign.save()

    def view(self):
        Advertising.objects.filter(id=self.id).update(views=F("views")+1)

        if self.payment_type == "CPM":
            self.campaign.ammount_spent = self.campaign.ammount_spent + Money((self.cpm_price.amount/1000), CAD)
            self.campaign.save()

    def image_thumb(self):
        return u'<img src="%s" height="60" />' % self.image.url

    image_thumb.short_description = 'Image'
    image_thumb.allow_tags = True


class BonusAdvertisingTransaction(models.Model):
    budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    campaign = models.ForeignKey(AdvertisingCampaign)
    processed_at = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)


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

    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    taxes = models.ManyToManyField("accounts.AccountTaxCost")

    def __unicode__(self):
        return "Order for %s" % self.campaign

    @property
    def cost_value(self):
        return self.budget


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
