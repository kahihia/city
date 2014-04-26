from django.contrib import admin
from django.template.defaultfilters import slugify
from django.http import HttpResponse

from django_exportable_admin.admin import CSVExportableAdmin, ExportableAdmin

from .models import Page
from .utils import htmldecode

admin.site.register(Page)


class FusionExportableAdmin(CSVExportableAdmin):
    def changelist_view(self, request, extra_context=None):
        if extra_context and extra_context['export_delimiter']:
            request.is_export_request = True
            base_response = super(ExportableAdmin, self).changelist_view(request, extra_context)
            base_response.template_name = 'django_exportable_admin/change_list_csv.html'
            base_response.render()
            response = HttpResponse(htmldecode(base_response.content), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(self.model._meta.verbose_name)
            return response
        extra_context = extra_context or {}
        extra_context.update({
            'export_buttons' : self.get_export_buttons(request),
        })
        return super(ExportableAdmin, self).changelist_view(request, extra_context)