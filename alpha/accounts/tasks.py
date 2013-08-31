from datetime import datetime, timedelta
from celery import task
from utils import remind_account_about_events, inform_account_about_events_with_tags
from models import AccountReminding, Account, InTheLoopSchedule
from event.models import SingleEvent


@task
def remind_accounts_about_events():
    hots = AccountReminding.hots.all()

    for reminding in hots:
        remind_account_about_events(reminding.account, SingleEvent.future_events.filter(id=reminding.single_event.id))
        reminding.processed()
    return hots


@task
def remind_accounts_about_events_on_week_day():
    for account in Account.objects.filter(reminder_active_type="WEEKDAY", reminder_on_week_day=str(datetime.now().weekday())):
        single_events = account.reminder_single_events.filter(start_time__gte=datetime.now(), start_time__lte=(datetime.now() + timedelta(days=7)))

        if len(single_events) > 0:
            remind_account_about_events(account, single_events)


@task
def inform_accounts_about_new_events_with_tags():
    # Optimize
    for account in Account.objects.all():
        inform_account_about_events_with_tags(account)

    InTheLoopSchedule.new_events.all().update(processed=True)
