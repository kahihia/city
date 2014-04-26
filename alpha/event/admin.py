from django.contrib import admin
from django.utils.html import format_html

from event.models import (Event,
                          SingleEvent,
                          AuditEvent,
                          AuditSingleEvent,
                          AuditPhrase,
                          FakeAuditEvent,
                          FeaturedEvent,
                          FeaturedEventOrder)
from event.models import Venue
from home.admin import FusionExportableAdmin


def approve_events(modeladmin, request, queryset):
    for audit_event in queryset:
        audit_event_fake = FakeAuditEvent.objects.get(pk=audit_event.pk)
        event_obj = Event.events.get(pk=audit_event.pk)
        audit_event.phrases.clear()
        audit_event_fake.delete()

        event_obj.audited = True
        event_obj.save()
approve_events.short_description = "Approve selected events"


class EventAdmin(FusionExportableAdmin):
    list_display = ('name', 'tags_list', 'city_name', 'venue_name', 'event_owner', 'created')
    fields = ('owner', 'venue_account_owner', 'email',
              'name', 'description', 'venue', 'price', 'website', 'tickets',
              'audited', 'tags',)
    change_form_template = 'events/edit/admin_edit_event.html'
    export_formats = (
        (u'CSV', u','),
    )

    def city_name(self, object):
        return object.venue.city.name if object.venue else ''

    def tags_list(self, object):
        return object.tags_representation()

    def venue_name(self, object):
        if object.venue_account_owner:
            return format_html('<a target="_blank" href="{0}">{1}</a>',
                               object.venue_account_owner.get_absolute_url(),
                               object.venue_account_owner.venue.name)
        else:
            return ''

    def event_owner(self, object):
        return object.owner

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'event_link': obj.get_absolute_url()
        })

        return super(EventAdmin, self).render_change_form(request, context, add=add,
                                                          change=change, form_url=form_url, obj=obj)

    tags_list.short_description = 'Tags'
    city_name.short_description = 'City'
    event_owner.short_description = 'User'
    venue_name.short_description = 'Venue'

    city_name.admin_order_field  = 'venue__city'
    venue_name.admin_order_field = 'venue_account_owner__venue__name'
    event_owner.admin_order_field = 'owner'

    def queryset(self, request):
        # Prefetch related objects
        return super(EventAdmin, self).queryset(request).select_related('venue', 'venue_account_owner')


class AuditEventAdmin(admin.ModelAdmin):
    actions = [approve_events]
    fields = ('name', 'description', 'owner', 'venue', )
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
admin.site.register(FeaturedEvent)

admin.site.register(FeaturedEventOrder)