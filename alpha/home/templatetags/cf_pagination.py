from django import template
register = template.Library()

@register.inclusion_tag('pagination.html', takes_context=True)
def cf_pagination(context):
    return context