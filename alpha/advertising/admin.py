from django.contrib import admin
from advertising.models import AdvertisingType, Advertising, AdvertisingCampaign, AdvertisingOrder, AdvertisingPayment


class AdvertisingTypeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'cpm_price', 'cpc_price')


class AdvertisingAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'image_thumb', 'review_status')
    readonly_fields = ('image_thumb',)


admin.site.register(AdvertisingType, AdvertisingTypeAdmin)
admin.site.register(Advertising, AdvertisingAdmin)
admin.site.register(AdvertisingCampaign)
admin.site.register(AdvertisingOrder)
admin.site.register(AdvertisingPayment)
