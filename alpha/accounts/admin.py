from django.contrib import admin
from django import forms
from userena.utils import get_user_model
from userena.admin import UserenaAdmin
from userena import settings as userena_settings
from accounts.models import AccountReminding, InTheLoopSchedule, VenueAccount, VenueType, AccountTax, AccountTaxCost


class VenueAccountAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'types':
            kwargs['widget'] = forms.CheckboxSelectMultiple
            kwargs['help_text'] = ''

        return db_field.formfield(**kwargs)


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
