from django.contrib import admin
from event.models import Event, SingleEvent, AuditEvent, AuditSingleEvent, AuditPhrase, FakeAuditEvent
from event.models import Venue
from event.models import Reminder


def approve_events(modeladmin, request, queryset):
    for audit_event in queryset:
        audit_event_fake = FakeAuditEvent.objects.get(pk=audit_event.pk)
        event_obj = Event.events.get(pk=audit_event.pk)
        audit_event.phrases.clear()
        audit_event_fake.delete()

        event_obj.audited = True
        event_obj.save()
approve_events.short_description = "Approve selected events"


class AuditEventAdmin(admin.ModelAdmin):
    actions = [approve_events]
    fields = ('name', 'description', 'owner', 'picture', 'venue', )
    list_display = ('name', 'description', 'owner')

    change_form_template = "audit/change_form.html"

    def has_add_permission(self, request):
        return False

admin.site.register(Event)
admin.site.register(SingleEvent)

admin.site.register(AuditPhrase)
admin.site.register(AuditEvent, AuditEventAdmin)
admin.site.register(AuditSingleEvent)
admin.site.register(Venue)
admin.site.register(Reminder)
