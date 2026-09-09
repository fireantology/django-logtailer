import json
import os
import shutil
import tempfile

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext as _

from logtailer.admin import LogFileAdminForm
from logtailer.models import LogFile
from logtailer.tests.utils import (
    create_staff_user, create_superuser, make_temp_log)
from logtailer.utils import is_path_allowed


class IsPathAllowedTest(SimpleTestCase):
    """Unit tests for the LOGTAILER_ALLOWED_ROOTS path check (issue #22)."""

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    @override_settings()
    def test_no_setting_denies_everything(self):
        # Secure by default: the setting is mandatory.
        from django.conf import settings
        del settings.LOGTAILER_ALLOWED_ROOTS
        self.assertFalse(is_path_allowed('/etc/passwd'))
        self.assertFalse(is_path_allowed(os.path.join(self.root, 'app.log')))

    def test_path_inside_root_is_allowed(self):
        with override_settings(LOGTAILER_ALLOWED_ROOTS=[self.root]):
            self.assertTrue(
                is_path_allowed(os.path.join(self.root, 'app.log')))
            self.assertTrue(
                is_path_allowed(os.path.join(self.root, 'sub', 'app.log')))

    def test_path_outside_root_is_denied(self):
        with override_settings(LOGTAILER_ALLOWED_ROOTS=[self.root]):
            self.assertFalse(is_path_allowed('/etc/passwd'))

    def test_empty_list_denies_everything(self):
        with override_settings(LOGTAILER_ALLOWED_ROOTS=[]):
            self.assertFalse(
                is_path_allowed(os.path.join(self.root, 'app.log')))

    def test_traversal_is_resolved_before_checking(self):
        with override_settings(LOGTAILER_ALLOWED_ROOTS=[self.root]):
            self.assertFalse(
                is_path_allowed(os.path.join(self.root, '..', 'etc', 'passwd')))

    def test_sibling_directory_with_same_prefix_is_denied(self):
        # /tmp/root-evil must not match allowed root /tmp/root.
        with override_settings(LOGTAILER_ALLOWED_ROOTS=[self.root]):
            self.assertFalse(is_path_allowed(self.root + '-evil/app.log'))

    def test_symlink_pointing_outside_root_is_denied(self):
        outside = make_temp_log('secret\n')
        self.addCleanup(os.remove, outside)
        link = os.path.join(self.root, 'link.log')
        os.symlink(outside, link)
        with override_settings(LOGTAILER_ALLOWED_ROOTS=[self.root]):
            self.assertFalse(is_path_allowed(link))

    def test_multiple_roots(self):
        other_root = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, other_root, ignore_errors=True)
        with override_settings(
                LOGTAILER_ALLOWED_ROOTS=[self.root, other_root]):
            self.assertTrue(
                is_path_allowed(os.path.join(other_root, 'app.log')))


class AllowedRootsTestCase(TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.enterContext(
            override_settings(LOGTAILER_ALLOWED_ROOTS=[self.root]))

    def make_allowed_log_file(self, content='one\ntwo\n'):
        path = os.path.join(self.root, 'app.log')
        with open(path, 'w') as f:
            f.write(content)
        return path, LogFile.objects.create(name='app', path=path)

    def make_denied_log_file(self):
        path = make_temp_log('secret\n')
        self.addCleanup(os.remove, path)
        return path, LogFile.objects.create(name='outside', path=path)


class GetLogLinesAllowedRootsTest(AllowedRootsTestCase):
    def setUp(self):
        super().setUp()
        create_staff_user()
        self.client.login(username='staff', password='password')

    def get_lines(self, file_id, **params):
        url = reverse('logtailer_get_log_lines', args=[file_id])
        response = self.client.get(url, params)
        return json.loads(response.content)

    def test_file_inside_root_is_readable(self):
        path, log_file = self.make_allowed_log_file()
        payload = self.get_lines(log_file.pk, history=2)
        self.assertEqual(payload, ['one<br/>', 'two<br/>'])

    def test_file_outside_root_is_denied(self):
        path, log_file = self.make_denied_log_file()
        for params in ({}, {'history': 5}):
            payload = self.get_lines(log_file.pk, **params)
            self.assertEqual(payload, [_('error_path_not_allowed')])


class DownloadAllowedRootsTest(AllowedRootsTestCase):
    def setUp(self):
        super().setUp()
        create_superuser()
        self.client.login(username='admin', password='password')

    def test_download_inside_root_works(self):
        path, log_file = self.make_allowed_log_file(content='data\n')
        url = reverse('admin:logtailer_logfile_download', args=[log_file.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'data\n')

    def test_download_outside_root_redirects_with_error(self):
        path, log_file = self.make_denied_log_file()
        url = reverse('admin:logtailer_logfile_download', args=[log_file.pk])
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse('admin:logtailer_logfile_change', args=[log_file.pk]))
        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertEqual(len(messages), 1)
        self.assertIn(_('error_path_not_allowed'), messages[0])


class LogFileAdminFormTest(AllowedRootsTestCase):
    def test_path_inside_root_validates(self):
        form = LogFileAdminForm(
            data={'name': 'app',
                  'path': os.path.join(self.root, 'app.log')})
        self.assertTrue(form.is_valid(), form.errors)

    def test_path_outside_root_is_rejected(self):
        form = LogFileAdminForm(
            data={'name': 'evil', 'path': '/etc/passwd'})
        self.assertFalse(form.is_valid())
        self.assertIn(_('error_path_not_allowed'),
                      form.errors['path'])
