from django.contrib.gis.db import models
from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager
from cities.models import Region


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


class AdvertisingCampaign(models.Model):
    name = models.CharField(max_length=128)
    account = models.ForeignKey('accounts.Account')
    all_of_canada = models.BooleanField()
    regions = models.ManyToManyField(Region)
    budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    ammount_spent = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    ammount_remaining = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    started = models.DateTimeField(auto_now=True, auto_now_add=True)
    ended = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    website = models.URLField()

    objects = money_manager(models.Manager())

    def __unicode__(self):
        return self.name


PAYMENT_TYPE = (
    ('CPM', 'CPM'),
    ('CPC', 'CPC'),
)


class Advertising(models.Model):
    ad_type = models.ForeignKey(AdvertisingType)
    campaign = models.ForeignKey(AdvertisingCampaign)
    payment_type = models.CharField(max_length=3, choices=PAYMENT_TYPE)
    image = models.ImageField(upload_to="advertising")
    reviewed = models.BooleanField(default=False)

    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    # Copy when create campaign. We should not change price after creating
    cpm_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    cpc_price = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    def __unicode__(self):
        return "%s - %s: %d/%d" % (self.campaign, self.ad_type, self.views, self.clicks)

    def click(self):
        # TODO: calculate cost
        self.clicks = self.clicks + 1
        self.save()

    def view(self):
        self.views = self.views + 1
        self.save()
