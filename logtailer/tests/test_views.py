import json
import os
import tempfile

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from logtailer.models import LogFile, LogsClipboard
from logtailer.tests.utils import create_staff_user, make_temp_log


class StaffRequiredTest(TestCase):
    """All logtailer views are protected by staff_member_required."""

    def setUp(self):
        self.log_file = LogFile.objects.create(name='app', path='/tmp/app.log')
        self.urls = [
            reverse('logtailer_read_logs'),
            reverse('logtailer_get_log_lines', args=[self.log_file.pk]),
            reverse('logtailer_save_to_clipboard'),
        ]

    def assert_all_redirect_to_login(self):
        for url in self.urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn('/admin/login/', response['Location'])

    def test_anonymous_user_is_redirected(self):
        self.assert_all_redirect_to_login()

    def test_non_staff_user_is_redirected(self):
        user = create_staff_user(username='regular')
        user.is_staff = False
        user.save()
        self.client.login(username='regular', password='password')
        self.assert_all_redirect_to_login()


class LogtailerViewTestCase(TestCase):
    def setUp(self):
        create_staff_user()
        self.client.login(username='staff', password='password')

    def make_log_file(self, content, name='test log'):
        path = make_temp_log(content)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return path, LogFile.objects.create(name=name, path=path)

    def get_lines(self, file_id, **params):
        url = reverse('logtailer_get_log_lines', args=[file_id])
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        return response, json.loads(response.content)


class ReadLogsViewTest(LogtailerViewTestCase):
    def test_renders_log_reader_template(self):
        response = self.client.get(reverse('logtailer_read_logs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logtailer/log_reader.html')
        self.assertIn('text/html', response['Content-Type'])


class GetLogLinesViewTest(LogtailerViewTestCase):
    def test_unknown_logfile_id_returns_error(self):
        response, payload = self.get_lines(9999)
        self.assertEqual(payload, [_('error_logfile_notexist')])

    def test_missing_file_on_disk_returns_error(self):
        # Path is inside an allowed root but does not exist on disk.
        log_file = LogFile.objects.create(
            name='ghost',
            path=os.path.join(
                tempfile.gettempdir(), 'logtailer-nonexistent.log'))
        response, payload = self.get_lines(log_file.pk)
        self.assertEqual(payload, [_('error_no_suchfile')])

    def test_history_returns_last_lines_html_formatted(self):
        path, log_file = self.make_log_file('one\ntwo\nthree\nfour\n')
        response, payload = self.get_lines(log_file.pk, history=2)
        self.assertEqual(payload, ['three<br/>', 'four<br/>'])
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_first_tail_call_returns_nothing_and_stores_position(self):
        path, log_file = self.make_log_file('one\ntwo\n')
        response, payload = self.get_lines(log_file.pk)
        self.assertEqual(payload, [])
        self.assertEqual(
            self.client.session['file_position_%s' % log_file.pk],
            os.path.getsize(path))

    def test_tail_returns_only_new_lines_on_subsequent_calls(self):
        path, log_file = self.make_log_file('one\ntwo\n')
        self.get_lines(log_file.pk)  # records current EOF position
        with open(path, 'a') as f:
            f.write('three\nfour\n')
        response, payload = self.get_lines(log_file.pk)
        self.assertEqual(payload, ['three<br/>', 'four<br/>'])
        # And nothing new on the next call.
        response, payload = self.get_lines(log_file.pk)
        self.assertEqual(payload, [])

    def test_truncated_file_returns_nothing_and_resets_position(self):
        path, log_file = self.make_log_file('one\ntwo\nthree\nfour\n')
        self.get_lines(log_file.pk)
        with open(path, 'w') as f:
            f.write('new\n')
        response, payload = self.get_lines(log_file.pk)
        self.assertEqual(payload, [])
        self.assertEqual(
            self.client.session['file_position_%s' % log_file.pk],
            os.path.getsize(path))


class LogLineFilterTest(LogtailerViewTestCase):
    """Server-side regex filtering via the ?filter= parameter."""

    def test_history_returns_only_matching_lines(self):
        path, log_file = self.make_log_file(
            'ERROR one\nINFO two\nERROR three\n')
        response, payload = self.get_lines(
            log_file.pk, history=10, filter='ERROR')
        self.assertEqual(payload, ['ERROR one<br/>', 'ERROR three<br/>'])

    def test_tail_returns_only_matching_new_lines(self):
        path, log_file = self.make_log_file('old\n')
        self.get_lines(log_file.pk)  # record current EOF position
        with open(path, 'a') as f:
            f.write('ERROR boom\nINFO fine\n')
        response, payload = self.get_lines(log_file.pk, filter='ERROR')
        self.assertEqual(payload, ['ERROR boom<br/>'])

    def test_inline_flags_are_supported(self):
        path, log_file = self.make_log_file('ERROR one\ninfo two\n')
        response, payload = self.get_lines(
            log_file.pk, history=10, filter='(?i)error')
        self.assertEqual(payload, ['ERROR one<br/>'])

    def test_invalid_regex_falls_back_to_substring(self):
        path, log_file = self.make_log_file(
            'has [unclosed bracket\nother line\n')
        response, payload = self.get_lines(
            log_file.pk, history=10, filter='[unclosed')
        self.assertEqual(payload, ['has [unclosed bracket<br/>'])

    def test_filter_matches_raw_line_not_escaped_output(self):
        # Pattern contains '<', which only exists in the raw line;
        # the returned payload is escaped nonetheless.
        path, log_file = self.make_log_file(
            '<script>alert("x")</script>\nplain\n')
        response, payload = self.get_lines(
            log_file.pk, history=10, filter='<script>')
        self.assertEqual(
            payload,
            ['&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;<br/>'])


class EscapingTest(LogtailerViewTestCase):
    """Log content must never reach the client as active HTML (XSS)."""

    def test_history_lines_are_html_escaped(self):
        path, log_file = self.make_log_file(
            '<img src=x onerror=alert(1)> & "quotes"\n')
        response, payload = self.get_lines(log_file.pk, history=5)
        self.assertEqual(
            payload,
            ['&lt;img src=x onerror=alert(1)&gt; &amp; '
             '&quot;quotes&quot;<br/>'])

    def test_tail_lines_are_html_escaped(self):
        path, log_file = self.make_log_file('start\n')
        self.get_lines(log_file.pk)
        with open(path, 'a') as f:
            f.write('<b>bold</b>\n')
        response, payload = self.get_lines(log_file.pk)
        self.assertEqual(payload, ['&lt;b&gt;bold&lt;/b&gt;<br/>'])


class SaveToClipboardViewTest(LogtailerViewTestCase):
    def test_post_creates_clipboard_entry(self):
        log_file = LogFile.objects.create(name='app', path='/tmp/app.log')
        response = self.client.post(
            reverse('logtailer_save_to_clipboard'),
            {'name': 'my clip', 'notes': 'a note',
             'logs': 'line1<br/>line2', 'file': str(log_file.pk)})
        self.assertEqual(response.status_code, 200)
        clipboard = LogsClipboard.objects.get()
        self.assertEqual(clipboard.name, 'my clip')
        self.assertEqual(clipboard.notes, 'a note')
        self.assertEqual(clipboard.logs, 'line1<br/>line2')
        self.assertEqual(clipboard.log_file, log_file)
