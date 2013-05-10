from django.contrib import admin
from advertising.models import AdvertisingType, Advertising, AdvertisingCampaign

class AdvertisingTypeAdmin(admin.ModelAdmin):    
    list_display = ('__unicode__', 'cpm_price', 'cpc_price')    


admin.site.register(AdvertisingType, AdvertisingTypeAdmin)
admin.site.register(Advertising)
admin.site.register(AdvertisingCampaign)
