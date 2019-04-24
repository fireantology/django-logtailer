import os
import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from logtailer.models import LogsClipboard, LogFile
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from django.conf import settings

HISTORY_LINES = getattr(settings, 'LOGTAILER_HISTORY_LINES', 0)


@staff_member_required
def read_logs(request):
    context = {}
    return render_to_response('logtailer/log_reader.html',
                              context, 
                              RequestContext(request, {}),)


def get_history(f, lines=HISTORY_LINES):
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
            f.seek(0,0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes += block*buffer_size
        block -= 1
    return ''.join(data).splitlines(True)[-lines:]

@staff_member_required
def get_log_lines(request, file_id, history=False):
    try:
        file_record = LogFile.objects.get(id=file_id)
    except LogFile.DoesNotExist:
        return HttpResponse(json.dumps([_('error_logfile_notexist')]),
                            content_type='text/html')
    content = []
    file = open(file_record.path, 'r')

    if history:
        content = get_history(file)
        content = [line.replace('\n','<br/>') for line in content]
    else:
        last_position = request.session.get('file_position_%s' % file_id)
        file.seek(0, os.SEEK_END)
        if last_position and last_position <= file.tell():
            file.seek(last_position)

        for line in file:
            content.append('%s' % line.replace('\n','<br/>'))

    request.session['file_position_%s' % file_id] = file.tell()
    file.close()
    return HttpResponse(json.dumps(content), content_type='application/json')


@staff_member_required
def save_to_clipoard(request):
    LogsClipboard(name = request.POST['name'],
                           notes = request.POST['notes'],
                           logs = request.POST['logs'],
                           log_file = LogFile.objects\
                           .get(id=int(request.POST['file']))).save()
    return HttpResponse(_('loglines_saved'), content_type='text/html')
