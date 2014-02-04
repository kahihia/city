from django import template
from ..url_management import utils

register = template.Library()


@register.simple_tag(takes_context=False)
def url_by_identifier(identifier):
    return utils.url_by_identifier(identifier)