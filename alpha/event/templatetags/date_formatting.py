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
    now = datetime.datetime.now()
    hour = dense_date.time()
    #if hour.minute == 0:
    #    hour_format = '%-1I %p'
    #else:
    hour_format = '%-1I:%M %p'
    if dense_date.date() == now.date():
        return hour.strftime('Today at ' + hour_format)
    difference = dense_date.date() - now.date()
    if difference == datetime.timedelta(days=1):
        return hour.strftime('Tomorrow, ' + hour_format)
    if difference < datetime.timedelta(days=7-now.weekday()):
        return dense_date.strftime('%A, ' + hour_format)
    return dense_date.strftime('%A %B %-1d, ' + hour_format)
