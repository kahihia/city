from django.contrib import admin
from event.models import Event, SingleEvent, AuditEvent, AuditSingleEvent, AuditPhrase, FakeAuditEvent, FeaturedEvent
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


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'venue', 'tags_representation')
    fields = ('slug', 'picture', 'owner', 'venue_account_owner', 'email',
              'name', 'description', 'venue', 'price', 'website', 'tickets',
              'audited', 'tags',)


class AuditEventAdmin(admin.ModelAdmin):
    actions = [approve_events]
    fields = ('name', 'description', 'owner', 'picture', 'venue', )
    list_display = ('name', 'description', 'owner')

    change_form_template = "audit/change_form.html"

    def has_add_permission(self, request):
        return False


class VenueAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Event, EventAdmin)
admin.site.register(SingleEvent)

admin.site.register(AuditPhrase)
admin.site.register(AuditEvent, AuditEventAdmin)
admin.site.register(AuditSingleEvent)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Reminder)
admin.site.register(FeaturedEvent)
