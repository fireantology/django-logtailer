from django.contrib import admin
from django.conf import settings
from logtailer.models import LogFile, Filter, LogsClipboard

class LogFileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'path')
    
    class Media:
        js = (settings.MEDIA_URL+'logtailer/js/jquery.colorbox-min.js',)
        css = {
            'all': (settings.MEDIA_URL+'logtailer/css/colorbox.css',)
        }

class LogsClipboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'notes', 'log_file')
    readonly_fields = ('name', 'notes', 'logs', 'log_file')
    
admin.site.register(LogFile, LogFileAdmin)
admin.site.register(Filter)
admin.site.register(LogsClipboard, LogsClipboardAdmin)