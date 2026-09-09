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
        # Hint shown while filters are locked during reading (JS toggles it).
        self.assertContains(response, 'id="filter-locked-hint"')

    def test_add_page_has_no_log_reader(self):
        response = self.client.get(reverse('admin:logtailer_logfile_add'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="log-window"')

    def test_change_page_is_read_only(self):
        path, log_file = self.make_log_file()
        url = reverse('admin:logtailer_logfile_change', args=[log_file.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # View mode: no save buttons, log reader still present.
        self.assertNotContains(response, 'name="_save"')
        self.assertContains(response, 'id="log-window"')

    def test_change_post_is_rejected(self):
        path, log_file = self.make_log_file(name='original')
        url = reverse('admin:logtailer_logfile_change', args=[log_file.pk])
        response = self.client.post(
            url, {'name': 'hacked', 'path': log_file.path, '_save': 'Save'})
        self.assertEqual(response.status_code, 403)
        log_file.refresh_from_db()
        self.assertEqual(log_file.name, 'original')

    def test_add_still_works(self):
        log_path = make_temp_log('hello\n')
        self.addCleanup(os.remove, log_path)
        response = self.client.post(
            reverse('admin:logtailer_logfile_add'),
            {'name': 'new log', 'path': log_path, '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            LogFile.objects.filter(name='new log', path=log_path).exists())

    def test_delete_still_works(self):
        path, log_file = self.make_log_file()
        response = self.client.post(
            reverse('admin:logtailer_logfile_delete', args=[log_file.pk]),
            {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(LogFile.objects.filter(pk=log_file.pk).exists())

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
