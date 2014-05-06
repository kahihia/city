from django.contrib import admin
from django import forms

from userena.utils import get_user_model
from userena.admin import UserenaAdmin
from userena import settings as userena_settings

from accounts.models import (Account,
                             AccountReminding,
                             InTheLoopSchedule,
                             VenueAccount,
                             VenueType,
                             AccountTax,
                             AccountTaxCost)
from home.admin import FusionExportableAdmin


class AccountAdmin(admin.ModelAdmin):
    fields = ('user', 'tax_origin_confirmed', 'not_from_canada', 'website')


class VenueAccountAdmin(FusionExportableAdmin):
    list_display = ('venue_name', 'venue_address', 'city_name', 'venue_phone', 'venue_email', 'venue_fax', 'venue_site')
    export_formats = (
        (u'CSV', u','),
    )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'types':
            kwargs['widget'] = forms.CheckboxSelectMultiple
            kwargs['help_text'] = ''

        return db_field.formfield(**kwargs)

    def venue_name(self, object):
        return object.venue.name

    def venue_address(self, object):
        return object.venue.address

    def city_name(self, object):
        return object.venue.city.name

    def venue_phone(self, object):
        return object.phone

    def venue_email(self, object):
        return object.email

    def venue_fax(self, object):
        return object.fax

    def venue_site(self, object):
        return object.site

    venue_name.short_description = 'Venue'
    venue_address.short_description = 'Address'
    city_name.short_description = 'City'
    venue_phone.short_description = 'Phone'
    venue_email.short_description = 'Email'
    venue_fax.short_description = 'Fax'
    venue_site.short_description = 'Web site'

    city_name.admin_order_field  = 'venue__city'

    def queryset(self, request):
        # Prefetch related objects
        return super(VenueAccountAdmin, self).queryset(request).select_related('venue')


class CityFusionUserAdmin(UserenaAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'date_joined', 'last_login')


admin.site.unregister(Account)
admin.site.register(Account, AccountAdmin)
admin.site.register(AccountReminding)
admin.site.register(AccountTax)
admin.site.register(AccountTaxCost)
admin.site.register(InTheLoopSchedule)
admin.site.register(VenueType)
admin.site.register(VenueAccount, VenueAccountAdmin)

if userena_settings.USERENA_REGISTER_USER:
    try:
        admin.site.unregister(get_user_model())
    except admin.sites.NotRegistered:
        pass

    admin.site.register(get_user_model(), CityFusionUserAdmin)
