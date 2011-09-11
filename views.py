import os
import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from logtailer.models import LogsClipboard, LogFile
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required


def read_logs(request):
    context = {}
    return render_to_response('logtailer/readlogs.html',
                              context, 
                              RequestContext(request, {}),)
    
def get_log_line(request,file_id):
    try:
        file_record = LogFile.objects.get(id=file_id)
    except LogFile.DoesNotExist:
        return HttpResponse(json.dumps([_('error_logfile_notexist')]),
                            mimetype = 'text/html')
    
    file = open(file_record.path, 'r')
    file_position = cache.get('file_position_%s' % file_id);
    file.seek(0, os.SEEK_END)
    if file_position and file_position<=file.tell():
        file.seek(file_position)
    
    content = []
    for line in file:
        content.append('%s' % line.replace('\n','<br/>'))
    
    cache.set('file_position_%s' % file_id, file.tell(), 60*10)
    file.close()
    return HttpResponse(json.dumps(content), mimetype = 'application/json')

@csrf_exempt
def save_to_cliboard(request):
    object = LogsClipboard(name = request.POST['name'],
                           notes = request.POST['notes'],
                           logs = request.POST['logs'],
                           log_file = LogFile.objects\
                           .get(id=int(request.POST['file'])))
    object.save()
    return HttpResponse(_('loglines_saved'), mimetype = 'text/html')
    
  
    
staff_member_required(read_logs)
staff_member_required(get_log_line)