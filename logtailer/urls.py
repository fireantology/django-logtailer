from django.conf.urls import url, patterns

urlpatterns = patterns('logtailer.views',
    url(r'^readlogs/$', 'read_logs'),
    url(r'^get-log-line/(?P<file_id>\d+)/$', 'get_log_lines', name='logtailer_get_log_lines'),
    url(r'^get-history/(?P<file_id>\d+)/$', 'get_log_lines', {'history': True}, name='logtailer_get_history'),
    url(r'^save-to-clipboard/$', 'save_to_cliboard', name="logtailer_save_to_clipboard"),
)
