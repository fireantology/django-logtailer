from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

urlpatterns = patterns('',
    url(r'^readlogs/$', 'logtailer.views.read_logs'),
    url(r'^get-log-line/(?P<file_id>\d+)/$', 'logtailer.views.get_log_line'),
    url(r'^save-to-clipboard/$',
         'logtailer.views.save_to_cliboard',
         name = "logtailer_save_to_clipboard"),
)
