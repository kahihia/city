from django import template
register = template.Library()


@register.inclusion_tag('advertising/setup/types.html', takes_context=True)
def setup_advertising_types(context):
    return context

@register.inclusion_tag('advertising/setup/upload.html', takes_context=True)
def setup_advertising_upload(context):
    return context

@register.inclusion_tag('advertising/setup/regions.html', takes_context=True)
def setup_advertising_regions(context):
    return context

@register.inclusion_tag('advertising/setup/payments.html', takes_context=True)
def setup_advertising_payments(context):
    return context

@register.inclusion_tag('advertising/setup/free_budget.html', takes_context=True)
def setup_advertising_free_budget(context):
    return context    