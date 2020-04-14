from django.contrib import admin
from logtailer.models import LogFile, Filter, LogsClipboard


class LogFileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'path')
    
    class Media:
        js = ('logtailer/js/jquery.colorbox.js',)
        css = {
            'all': ('logtailer/css/colorbox.css',
                    'logtailer/css/logtailer.css',)
        }


class FilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'regex')   


class LogsClipboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'notes', 'log_file')
    readonly_fields = ('name', 'notes', 'logs', 'log_file')


admin.site.register(LogFile, LogFileAdmin)
admin.site.register(Filter, FilterAdmin)
admin.site.register(LogsClipboard, LogsClipboardAdmin)