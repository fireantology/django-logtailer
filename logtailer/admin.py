from django.contrib import admin
from django.utils.translation import gettext as _
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from logtailer.models import LogFile, Filter, LogsClipboard


class LogFileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'path')

    class Media:
        css = {
            'all': ('logtailer/css/logtailer.css',)
        }

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()
        my_urls = [
            path('<int:object_id>/download/',
                self.admin_site.admin_view(self.download), {},
                name="%s_%s_download" % info),
        ]
        return my_urls + urls

    def download(self, request, object_id):
        try:
            log_file = self.get_object(request, object_id)
            with open(log_file.path, 'r') as f:
                buffer = f.read()
            response = HttpResponse(buffer, content_type='plain/text')
            response['Content-Disposition'] = 'attachment; filename=%s' % log_file.name
        except Exception as e:
            try:
                from django.contrib import messages
                self.message_user(request, _('ERROR') + ': ' + str(e), level=messages.ERROR)
            except:
                pass
            response = HttpResponseRedirect(reverse('admin:logtailer_logfile_change', args=(object_id, )))
        return response


class FilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'regex')


class LogsClipboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'notes', 'log_file')
    readonly_fields = ('name', 'notes', 'logs', 'log_file')


admin.site.register(LogFile, LogFileAdmin)
admin.site.register(Filter, FilterAdmin)
admin.site.register(LogsClipboard, LogsClipboardAdmin)
