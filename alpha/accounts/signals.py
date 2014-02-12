from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django_facebook.utils import clear_persistent_graph_cache
from django.db.models.signals import post_save, m2m_changed
from django.db.models import F

from guardian.shortcuts import assign
from userena.managers import ASSIGNED_PERMISSIONS

from event.models import SingleEvent
from .models import Account, AccountReminding, BonusCampaign, REMINDER_TYPES
from .services import reminding_service


def after_login(sender, user, request, **kwargs):
    if request.GET.get('facebook_login', False):
        profile = user.get_profile()
        if not profile.new_token_required and profile.access_token:
            user.get_profile().extend_access_token()


def after_logout(sender, user, request, **kwargs):
    clear_persistent_graph_cache(request)


def after_account_save(sender, instance, created, **kwargs):
    if created:
        if instance.user.email:
            reminding_service.update_reminder_emails(instance, instance.user.email)

        copy_occurring_bonus(instance)


def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        user = instance
        account = Account.objects.create(user=user)

        for perm in ASSIGNED_PERMISSIONS['profile']:
            assign(perm[0], user, account)

        for perm in ASSIGNED_PERMISSIONS['user']:
            assign(perm[0], user, user)


def copy_occurring_bonus(account):
    for bonus_campaign in BonusCampaign.occurring_bonuses.all():
        Account.objects.filter(id=account.id).update(
            bonus_budget=F("bonus_budget")+bonus_campaign.budget.amount
        )


def sync_schedule_after_reminder_single_events_was_modified(sender, **kwargs):
    if kwargs['action'] == 'post_add':
        events = SingleEvent.future_events.filter(id__in=kwargs["pk_set"])

        for reminder_type in REMINDER_TYPES:
            if kwargs['instance'].check_reminder_type_state(reminder_type):
                reminding_service.add_single_events_to_schedule(kwargs['instance'], events, reminder_type)

    if kwargs['action'] == 'post_remove':
        AccountReminding.objects.filter(single_event__id__in=kwargs["pk_set"]).delete()


def sync_schedule_after_reminder_settings_was_changed(sender, instance, created, **kwargs):
    AccountReminding.objects.filter(account_id=instance.id).delete()
    for reminder_type in REMINDER_TYPES:
        if instance.check_reminder_type_state(reminder_type):
            reminding_service.add_single_events_to_schedule(instance,
                                                            instance.reminder_single_events.all(),
                                                            reminder_type)

user_logged_in.connect(after_login)
user_logged_out.connect(after_logout)

post_save.connect(create_facebook_profile, sender=User)
post_save.connect(after_account_save, sender=Account)
post_save.connect(sync_schedule_after_reminder_settings_was_changed, sender=Account)

m2m_changed.connect(sync_schedule_after_reminder_single_events_was_modified,
                    sender=Account.reminder_single_events.through)