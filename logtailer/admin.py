from django import forms
from django.contrib import admin
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from logtailer.models import LogFile, Filter, LogsClipboard
from logtailer.utils import is_path_allowed


class LogFileAdminForm(forms.ModelForm):
    class Meta:
        model = LogFile
        fields = '__all__'

    def clean_path(self):
        file_path = self.cleaned_data['path']
        if not is_path_allowed(file_path):
            raise forms.ValidationError(
                gettext_lazy('error_path_not_allowed'))
        return file_path


class LogFileAdmin(admin.ModelAdmin):
    form = LogFileAdminForm
    list_display = ('name', 'path')

    def has_change_permission(self, request, obj=None):
        # LogFile records can be added and deleted but not edited: the
        # detail page is a read-only log viewer. Replace a log file by
        # adding a new record and deleting the old one.
        return False

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
            if not is_path_allowed(log_file.path):
                raise PermissionError(_('error_path_not_allowed'))
            with open(log_file.path, 'r', errors='replace') as f:
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
