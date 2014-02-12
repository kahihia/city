import datetime
from datetime import timedelta
from ..models import AccountReminding


def update_reminder_emails(account, email):
    """ Update reminder and in the loop emails.

    @type account: accounts.models.Account
    @type email: unicode
    """
    account.reminder_email = email
    account.in_the_loop_email = email
    account.save(update_fields=['reminder_email', 'in_the_loop_email'])


def add_single_events_to_schedule(account, events, reminder_type):
    for event_day in events:
        if reminder_type == 'DAYS' and account.reminder_days_before_event:
            _add_days_reminder(account, event_day)

        if reminder_type == 'HOURS' and account.reminder_hours_before_event:
            _add_hours_reminder(account, event_day)

        if reminder_type == 'EACH_DAY' and account.reminder_each_day_from:
            _add_each_day_reminder(account, event_day)


def _add_days_reminder(account, single_event):
    notification_time = single_event.start_time - timedelta(days=int(account.reminder_days_before_event))
    _add_reminder(account, single_event, notification_time, 'DAYS_BEFORE_EVENT')


def _add_hours_reminder(account, single_event):
    notification_time = single_event.start_time - timedelta(hours=int(account.reminder_hours_before_event))
    _add_reminder(account, single_event, notification_time, 'HOURS_BEFORE_EVENT')


def _add_each_day_reminder(account, single_event):
    if account.reminder_each_day_from:
        for day_num in range(account.reminder_each_day_from, 0, -1):
            notification_time = (single_event.start_time - timedelta(days=day_num))\
                .replace(hour=account.reminder_each_day_at_time.hour,
                         minute=account.reminder_each_day_at_time.minute)
            _add_reminder(account, single_event, notification_time, 'DAYS_BEFORE_EVENT')


def _add_reminder(account, single_event, notification_time, notification_type):
    if notification_time and notification_time > datetime.datetime.now():
        reminding = AccountReminding(
            account=account,
            single_event=single_event,
            notification_time=notification_time,
            notification_type=notification_type
        )
        reminding.save()