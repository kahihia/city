from django import forms
from django.contrib import admin
from event.models import Event, SingleEvent, AuditEvent, AuditSingleEvent, AuditPhrase, FakeAuditEvent, FeaturedEvent
from event.models import Venue
from event.models import Reminder
from event.services import facebook_service


def approve_events(modeladmin, request, queryset):
    for audit_event in queryset:
        audit_event_fake = FakeAuditEvent.objects.get(pk=audit_event.pk)
        event_obj = Event.events.get(pk=audit_event.pk)
        audit_event.phrases.clear()
        audit_event_fake.delete()

        event_obj.audited = True
        event_obj.save()
approve_events.short_description = "Approve selected events"


class EventAdminForm(forms.ModelForm):

    test_field = forms.CharField()

    class Meta:
        model = Event


class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ('name', 'description', 'venue', 'tags_representation')
    fields = ('slug', 'picture', 'owner', 'venue_account_owner', 'email',
              'name', 'description', 'venue', 'price', 'website', 'tickets',
              'audited', 'post_to_facebook', 'tags', 'test_field')

    def save_model(self, request, obj, form, change):
        raise Exception(form.cleaned_data)
        super(EventAdmin, self).save_model(request, obj, form, change)
        if obj.post_to_facebook and not obj.facebook_event:
            facebook_service.create_facebook_event(None, obj, request)


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
