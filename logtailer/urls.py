from django.urls import path
from . import views

urlpatterns = [
    path('readlogs/', views.read_logs, name='logtailer_read_logs'),
    path('get-log-line/<int:file_id>/', views.get_log_lines, name='logtailer_get_log_lines'),
    path('save-to-clipboard/', views.save_to_clipoard, name="logtailer_save_to_clipboard"),
]
