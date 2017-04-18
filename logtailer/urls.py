from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^readlogs/$',
        views.read_logs,
        name='logtailer_read_logs'),
    url(r'^get-log-line/(?P<file_id>\d+)/$',
        views.get_log_lines,
        name='logtailer_get_log_lines'),
    url(r'^get-history/(?P<file_id>\d+)/$',
        views.get_log_lines,
        {'history': True},
        name='logtailer_get_history'),
    url(r'^save-to-clipboard/$',
        views.save_to_clipoard,
        name="logtailer_save_to_clipboard"),
]
