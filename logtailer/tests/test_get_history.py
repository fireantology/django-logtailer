import os

from django.test import SimpleTestCase

from logtailer.views import get_history
from logtailer.tests.utils import make_temp_log


class GetHistoryTest(SimpleTestCase):
    """Unit tests for the tail-like get_history() helper."""

    def open_log(self, content):
        path = make_temp_log(content)
        self.addCleanup(os.remove, path)
        f = open(path, 'r')
        self.addCleanup(f.close)
        return f

    def test_returns_last_n_lines(self):
        f = self.open_log('line1\nline2\nline3\nline4\nline5\n')
        self.assertEqual(get_history(f, 2), ['line4\n', 'line5\n'])

    def test_more_lines_requested_than_available(self):
        f = self.open_log('line1\nline2\n')
        self.assertEqual(get_history(f, 10), ['line1\n', 'line2\n'])

    def test_file_larger_than_buffer(self):
        # Each line is ~100 bytes so the file spans several 1024-byte buffers.
        lines = ['%03d %s\n' % (i, 'x' * 96) for i in range(100)]
        f = self.open_log(''.join(lines))
        self.assertEqual(get_history(f, 5), lines[-5:])

    def test_no_trailing_newline(self):
        f = self.open_log('line1\nline2\nlast line without newline')
        self.assertEqual(
            get_history(f, 2), ['line2\n', 'last line without newline'])

    def test_empty_file(self):
        f = self.open_log('')
        self.assertEqual(get_history(f, 5), [])

    def test_zero_lines_requested(self):
        f = self.open_log('line1\nline2\n')
        self.assertEqual(get_history(f, 0), [])
