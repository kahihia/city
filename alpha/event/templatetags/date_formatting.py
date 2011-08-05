from django import template
import datetime

register = template.Library()

@register.filter(name='contextualize_date')
def contextualize_date(dense_date=None):
    """
    Pre: dense_date is a DateTimeField

    Post: a human understandable string referencing the current
    time frame is generated from the DateTimeField

    Returns: the generated string
    """
    if not dense_date:
        return ''
    now = datetime.datetime.now()
    hour = dense_date.time()
    #if hour.minute == 0:
    #    hour_format = '%-1I %p'
    #else:
    hour_format = '%-1I:%M%p'
    if dense_date.date() == now.date():
        return hour.strftime('Today at ' + hour_format)
    difference = dense_date.date() - now.date()
    if difference == datetime.timedelta(days=1):
        return hour.strftime('Tomorrow, ' + hour_format)
    if difference < datetime.timedelta(days=7-now.weekday()):
        return dense_date.strftime('%A, ' + hour_format)
    return dense_date.strftime('%A %B %-1d, ' + hour_format)

@register.filter(name='just_day')
def just_day(dense_date=None):
    """
    Pre: dense_date is a DateTimeField
    Post: just the day as a unicode string
    Returns: the generated string
    """
    if not dense_date:
        return ''
    return dense_date.strftime('%A %B %-1d')

@register.filter(name='month_day')
def month_day(dense_date=None):
    if not dense_date:
        return ''
    return dense_date.strftime('%B %-1d')

@register.filter(name='just_time')
def just_time(dense_date=None):
    """
    Pre: dense_date is a DateTimeField
    Post: just the day as a unicode string
    Returns: the generated string
    """
    if not dense_date:
        return ''
    return dense_date.strftime('%-1I:%M %p')

@register.filter(name='just_time_levi_is_a_good_designer')
def just_time_levi_is_a_good_designer(dense_date=None):
    """
    Pre: dense_date is a DateTimeField
    Post: just the day as a unicode string
    Returns: the generated string
    """
    if not dense_date:
        return ''
    return dense_date.strftime('%-1I:%M%p')
