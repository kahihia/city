from celery import task
from django.db import transaction

from models import AdvertisingCampaign
from accounts.models import Account
from django.db.models import F


@transaction.commit_on_success
def return_unused_money_from_finished_acampaign(advertising_campaign):
    unused_money = advertising_campaign.ammount_remaining()

    Account.objects.filter(id=advertising_campaign.account_id).update(bonus_budget=F("bonus_budget")+unused_money.amount)
    advertising_campaign.budget = advertising_campaign.budget - unused_money
    advertising_campaign.save()


@task
def return_unused_money_to_bonus_for_advertising_campaigns():
    campaigns_with_unused_money = AdvertisingCampaign.with_unused_money.all()

    for advertising_campaign in campaigns_with_unused_money:
        return_unused_money_from_finished_acampaign(advertising_campaign)
