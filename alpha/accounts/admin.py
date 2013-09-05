from django.contrib import admin
from django import forms
from accounts.models import AccountReminding, InTheLoopSchedule, VenueAccount, VenueType, AccountTax, AccountTaxCost


class VenueAccountAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'types':
            kwargs['widget'] = forms.CheckboxSelectMultiple
            kwargs['help_text'] = ''

        return db_field.formfield(**kwargs)


admin.site.register(AccountReminding)
admin.site.register(AccountTax)
admin.site.register(AccountTaxCost)
admin.site.register(InTheLoopSchedule)
admin.site.register(VenueType)
admin.site.register(VenueAccount, VenueAccountAdmin)
