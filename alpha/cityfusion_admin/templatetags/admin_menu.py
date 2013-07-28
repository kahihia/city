from django import template

from cityfusion_admin.models import CF_ADMIN_MENU

register = template.Library()


@register.inclusion_tag('cf-admin/menu.html', takes_context=True)
def cf_admin_menu(context, active=None):    
        return {
            'menu_items': CF_ADMIN_MENU,
            'active': active
        }