from django import template

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

register = template.Library()


@register.simple_tag
def if_url(value, if_passed, if_failed):
    val = URLValidator()
    try:
        val(value)
        return if_passed
    except ValidationError:
        return if_failed
