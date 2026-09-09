import os
import tempfile

from django.test import TestCase
from django.urls import reverse

from logtailer.models import LogFile
from logtailer.tests.utils import create_superuser, make_temp_log


class LogFileAdminTestCase(TestCase):
    def setUp(self):
        create_superuser()
        self.client.login(username='admin', password='password')

    def make_log_file(self, content='hello\nworld\n', name='test.log'):
        path = make_temp_log(content)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return path, LogFile.objects.create(name=name, path=path)


class ChangeFormTest(LogFileAdminTestCase):
    def test_change_page_includes_log_reader(self):
        path, log_file = self.make_log_file()
        url = reverse('admin:logtailer_logfile_change', args=[log_file.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Log reader UI is included in the content area.
        self.assertContains(response, 'id="log-window"')
        self.assertContains(response, 'LOGTAILER_URL_GETLOGLINE')
        self.assertContains(
            response,
            reverse('logtailer_get_log_lines', args=[log_file.pk]))
        # Download link is in the object-tools.
        self.assertContains(
            response,
            reverse('admin:logtailer_logfile_download', args=[log_file.pk]))

    def test_add_page_has_no_log_reader(self):
        response = self.client.get(reverse('admin:logtailer_logfile_add'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="log-window"')

    def test_changelist_shows_name_and_path(self):
        path, log_file = self.make_log_file(name='my log file')
        response = self.client.get(
            reverse('admin:logtailer_logfile_changelist'))
        self.assertContains(response, 'my log file')
        self.assertContains(response, path)


class DownloadViewTest(LogFileAdminTestCase):
    def test_download_returns_file_as_attachment(self):
        path, log_file = self.make_log_file(content='log content here\n')
        url = reverse('admin:logtailer_logfile_download', args=[log_file.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'log content here\n')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn(log_file.name, response['Content-Disposition'])

    def test_download_replaces_undecodable_bytes(self):
        path, log_file = self.make_log_file()
        with open(path, 'wb') as f:
            f.write(b'valid\nbad \xff byte\n')
        url = reverse('admin:logtailer_logfile_download', args=[log_file.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content.decode(), 'valid\nbad \ufffd byte\n')

    def test_download_missing_file_redirects_with_error(self):
        # Path is inside an allowed root but does not exist on disk.
        log_file = LogFile.objects.create(
            name='ghost',
            path=os.path.join(
                tempfile.gettempdir(), 'logtailer-nonexistent.log'))
        url = reverse('admin:logtailer_logfile_download', args=[log_file.pk])
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse('admin:logtailer_logfile_change', args=[log_file.pk]))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn('ERROR', str(messages[0]))
