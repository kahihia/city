from datetime import datetime, timedelta
from celery import task
from utils import remind_account_about_events, inform_account_about_events_with_tag
from models import AccountReminding, Account, InTheLoopSchedule
from event.models import Event


@task
def remind_accounts_about_events():
    # TODO: select related
    hots = AccountReminding.hots.all()

    for reminding in hots:
        remind_account_about_events(reminding.account, Event.future_events.filter(id=reminding.event.id))
        reminding.processed()
    return hots


@task
def remind_accounts_about_events_on_week_day():
    # TODO: select related
    for account in Account.objects.filter(reminder_active_type="WEEKDAY", reminder_on_week_day=str(datetime.now().weekday())):
        event_ids = account.reminder_events.filter(single_events__start_time__gte=datetime.now(), single_events__start_time__lte=(datetime.now() + timedelta(days=7))).values_list("id", flat=True)
        events = Event.future_events.filter(id__in=event_ids)
        if len(events) > 0:
            remind_account_about_events(account, events)


@task
def inform_accounts_about_new_events_with_tags():
    # Optimize
    for account in Account.objects.all():
        events = InTheLoopSchedule.unprocessed_for_account(account)
        if events.count():
            account_tags = account.in_the_loop_tags.values_list('name', flat=True)
            tags_in_venues = {}
            for event in events:
                event_tags = event.tags.values_list('name', flat=True)

                tags_intersection = list(set(account_tags) & set(event_tags))

                for tag in tags_intersection:
                    if tag in tags_in_venues:
                        tags_in_venues[tag].append(event.venue.city.name_std)
                    else:
                        tags_in_venues[tag] = [event.venue.city.name_std]

            inform_account_about_events_with_tag(account, events, tags_in_venues)

    InTheLoopSchedule.new_events.all().update(processed=True)
