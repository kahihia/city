from datetime import datetime, timedelta
from celery import task
from home.utils import deserialize_json_deep

from utils import remind_account_about_events, inform_account_about_events_with_tags, remind_account_about_deleted_events
from models import AccountReminding, Account, InTheLoopSchedule
from event.models import SingleEvent
from accounts.models import REMINDER_TYPES


@task
def remind_accounts_about_events():
    hots = AccountReminding.hots.existing()

    for reminding in hots:
        remind_account_about_events(reminding.account, SingleEvent.future_events.filter(id=reminding.single_event.id))
        reminding.processed()
    return hots


@task
def remind_accounts_about_deleted_events():
    reminders = AccountReminding.hots.deleted()

    for reminder in reminders:
        single_events = deserialize_json_deep(reminder.archived_data, {'event': {'relations': ('venue',)}})
        remind_account_about_deleted_events(reminder.account, single_events)
        reminder.processed()

    return reminders


@task
def remind_accounts_about_events_on_week_day():
    accounts = Account.objects.extra(where=['reminder_type_state & %s != 0' % REMINDER_TYPES['WEEKDAY']['id']])\
                      .filter(reminder_on_week_day=str(datetime.now().weekday()))
    for account in accounts:
        single_events = account.reminder_single_events.filter(start_time__gte=datetime.now(), start_time__lte=(datetime.now() + timedelta(days=7)))

        if len(single_events) > 0:
            remind_account_about_events(account, single_events)


@task
def inform_accounts_about_new_events_with_tags():
    # Optimize
    for account in Account.objects.all():
        inform_account_about_events_with_tags(account)

    InTheLoopSchedule.new_events.all().update(processed=True)
