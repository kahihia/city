from datetime import datetime, timedelta
from celery import task
from utils import remind_account_about_events
from models import AccountReminding, Account


@task
def remind_accounts_about_events():
    # TODO: select related
    for reminding in AccountReminding.hots.all():
        remind_account_about_events(reminding.account, reminding.event)
        reminding.processed()


@task
def remind_accounts_about_events_on_week_day():
    # TODO: select related
    for account in Account.objects.filter(reminder_on_week_day=str(datetime.now().weekday())):
        events = account.reminder_events.filter(start_time__gte=datetime.now(), start_time__lte=(datetime.now() + timedelta(days=7)))
        if len(events) > 0:
            remind_account_about_events(account, events)


@task
def remind_accounts_about_new_events_with_tags_from_the_loop_on_week_day():
    for account in Account.objects.filter(in_the_loop_on_week_day=str(datetime.now().weekday())):
        pass
    # TODO: discuss implementation with customer
    # tags = [tag.name for tag in event.tags]
    # for account in Account.objects.filter(in_the_loop_tags__name__in=tags):
    #     remind_account_about_event_with_tag
