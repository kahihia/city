from django.contrib.gis.db import models
from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager
from cities.models import Region
from accounts.models import Account


class AdvertisingType(models.Model):
    name = models.CharField(max_length=128)
    width = models.DecimalField()
    height = models.DecimalField()
    cpm_price =  MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    cpc_price =  MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    objects = money_manager(models.Manager())


class AdvertisingCampaign(models.Model):
    name = models.CharField(max_length=128)
    account = models.ForeignKey(Account)
    all_of_canada = models.BooleanField()
    regions = models.ManyToManyField(Region)
    budget = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    ammount_spent = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    ammount_remaining = MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    # Copy when create campaign. We should not change price after creating
    cpm_price =  MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')
    cpc_price =  MoneyField(max_digits=10, decimal_places=2, default_currency='CAD')

    started = models.DateTimeField()
    ended = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    objects = money_manager(models.Manager())


PAYMENT_TYPE = (
    ('CPM', 'CPM'),
    ('CPC', 'CPC'),
)


class Advertising(models.Model):
    ad_type = models.ForeignKey(AdvertisingType)
    ad_company = models.ForeignKey(AdvertisingCampaign)
    payment_type = models.CharField(max_length=3, choices=PAYMENT_TYPE)
    ads_image = models.ImageField()
    reviewed = models.BooleanField(default=False)
