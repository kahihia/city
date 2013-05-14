from django.contrib import admin
from accounts.models import AccountReminding, InTheLoopSchedule, VenueAccount

admin.site.register(AccountReminding)
admin.site.register(InTheLoopSchedule)
admin.site.register(VenueAccount)
