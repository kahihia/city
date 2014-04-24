from django.contrib import admin
from django import forms

from userena.utils import get_user_model
from userena.admin import UserenaAdmin
from userena import settings as userena_settings
from django_exportable_admin.admin import CSVExportableAdmin

from accounts.models import AccountReminding, InTheLoopSchedule, VenueAccount, VenueType, AccountTax, AccountTaxCost


class VenueAccountAdmin(CSVExportableAdmin):
    list_display = ('venue', 'venue_address', 'venue_phone', 'venue_email', 'venue_fax', 'venue_site')
    export_formats = (
        (u'CSV', u','),
    )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'types':
            kwargs['widget'] = forms.CheckboxSelectMultiple
            kwargs['help_text'] = ''

        return db_field.formfield(**kwargs)

    def venue_address(self, object):
        return object.venue.address

    def venue_phone(self, object):
        return object.phone

    def venue_email(self, object):
        return object.email

    def venue_fax(self, object):
        return object.fax

    def venue_site(self, object):
        return object.site

    venue_address.short_description = 'Address'
    venue_phone.short_description = 'Phone'
    venue_email.short_description = 'Email'
    venue_fax.short_description = 'Fax'
    venue_site.short_description = 'Web site'

    def queryset(self, request):
        # Prefetch related objects
        return super(VenueAccountAdmin, self).queryset(request).select_related('venue')


class CityFusionUserAdmin(UserenaAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'date_joined', 'last_login')


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
