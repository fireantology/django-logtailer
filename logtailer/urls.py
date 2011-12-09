from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

urlpatterns = patterns('logtailer.views',
    url(r'^readlogs/$', 'read_logs'),
    url(r'^get-log-line/(?P<file_id>\d+)/$', 'get_log_line', name='logtailer_get_log_line'),
    url(r'^save-to-clipboard/$', 'save_to_cliboard', name="logtailer_save_to_clipboard"),
)
