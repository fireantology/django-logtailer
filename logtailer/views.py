import os
import json
import re
from django.http import HttpResponse
from django.shortcuts import render
from logtailer.models import LogsClipboard, LogFile
from logtailer.utils import is_path_allowed
from django.utils.html import escape
from django.utils.translation import gettext as _
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def read_logs(request):
    return render(request, 'logtailer/log_reader.html', {})


def get_history(f, lines=0):
    buffer_size = 1024
    f.seek(0, os.SEEK_END)
    bytes = f.tell()
    size = lines
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if bytes - buffer_size > 0:
            # Seek back one whole buffer_size
            f.seek(f.tell()+block*buffer_size, 0)
            # read buffer
            data.append(f.read(buffer_size))
        else:
            # file too small, start from beginning
            f.seek(0, 0)
            # only read what was not read
            data.append(f.read(bytes))
        lines_found = data[-1].count('\n')
        size -= lines_found
        bytes += block*buffer_size
        block -= 1
    return ''.join(data).splitlines(True)[-lines:]


def get_line_filter(pattern):
    """Build a predicate for raw log lines from a regex pattern.

    Returns None when no pattern is given (no filtering). Invalid regexes
    fall back to a literal substring match.
    """
    if not pattern:
        return None
    try:
        regex = re.compile(pattern)
    except re.error:
        return lambda line: pattern in line
    return lambda line: regex.search(line) is not None


def format_lines(lines, line_filter):
    """Filter raw lines, then escape HTML and convert newlines to <br/>.

    Filtering happens on the raw line so regexes match true log content;
    escaping afterwards prevents log content from being rendered as HTML
    (stored XSS).
    """
    return [str(escape(line)).replace('\n', '<br/>')
            for line in lines
            if line_filter is None or line_filter(line)]


@staff_member_required
def get_log_lines(request, file_id):
    history = int(request.GET.get('history', 0))
    line_filter = get_line_filter(request.GET.get('filter', ''))
    try:
        file_record = LogFile.objects.get(id=file_id)
    except LogFile.DoesNotExist:
        return HttpResponse(json.dumps([_('error_logfile_notexist')]),
                            content_type='text/html')
    if not is_path_allowed(file_record.path):
        return HttpResponse(json.dumps([_('error_path_not_allowed')]),
                            content_type='application/json')
    try:
        file = open(file_record.path, 'r', errors='replace')
    except FileNotFoundError:
        return HttpResponse(json.dumps([_('error_no_suchfile')]),)

    if history > 0:
        content = format_lines(get_history(file, history), line_filter)
    else:
        last_position = request.session.get('file_position_%s' % file_id)
        file.seek(0, os.SEEK_END)
        if last_position and last_position <= file.tell():
            file.seek(last_position)
        content = format_lines(file, line_filter)

    request.session['file_position_%s' % file_id] = file.tell()
    file.close()
    return HttpResponse(json.dumps(content), content_type='application/json')


@staff_member_required
def save_to_clipboard(request):
    LogsClipboard(name=request.POST['name'],
                  notes=request.POST['notes'],
                  logs=request.POST['logs'],
                  log_file=LogFile.objects.get(id=int(request.POST['file']))).save()
    return HttpResponse(_('loglines_saved'), content_type='text/html')
