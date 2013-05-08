from django.contrib import admin
from accounts.models import AccountReminding, InTheLoopSchedule

admin.site.register(AccountReminding)
admin.site.register(InTheLoopSchedule)
