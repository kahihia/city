from django import template
from ..utils import get_region_shortcut

register = template.Library()


@register.filter(name='region_shortcut')
def region_shortcut(region_name=None):
    return get_region_shortcut(region_name)