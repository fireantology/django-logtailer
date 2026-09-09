from django.test import TestCase

from logtailer.models import Filter, LogFile, LogsClipboard


class LogFileModelTest(TestCase):
    def test_str_returns_name(self):
        log_file = LogFile.objects.create(name='syslog', path='/var/log/syslog')
        self.assertEqual(str(log_file), 'syslog')


class FilterModelTest(TestCase):
    def test_str_contains_name_and_regex(self):
        log_filter = Filter.objects.create(name='errors', regex='ERROR.*')
        self.assertIn('errors', str(log_filter))
        self.assertIn('ERROR.*', str(log_filter))


class LogsClipboardModelTest(TestCase):
    def setUp(self):
        self.log_file = LogFile.objects.create(name='app', path='/tmp/app.log')

    def test_str_returns_name(self):
        clipboard = LogsClipboard.objects.create(
            name='snippet', notes='some notes', logs='line1\nline2',
            log_file=self.log_file)
        self.assertEqual(str(clipboard), 'snippet')

    def test_deleted_with_log_file(self):
        LogsClipboard.objects.create(
            name='snippet', logs='line1', log_file=self.log_file)
        self.log_file.delete()
        self.assertEqual(LogsClipboard.objects.count(), 0)
