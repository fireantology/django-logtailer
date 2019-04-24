from django.db import models
from django.utils.translation import ugettext_lazy as _


class LogFile(models.Model):
    name = models.CharField(_('name'), max_length=180)
    path = models.CharField(_('path'), max_length=500)
    
    def __unicode__(self):
        return '%s' % self.name
    
    class Meta:
        verbose_name = _('Log file')
        verbose_name_plural = _('Log files')


class Filter(models.Model):
    name = models.CharField(_('name'), max_length=180)
    regex = models.CharField(_('regex'), max_length=500)
    
    def __unicode__(self):
        return '%s | %s: %s ' % (self.name, _('pattern'), self.regex)
    
    class Meta:
        verbose_name = _('filter')
        verbose_name_plural = _('filters')


class LogsClipboard(models.Model):
    name = models.CharField(_('name'), max_length=180)
    notes = models.TextField(_('notes'), blank=True, null=True)
    logs = models.TextField(_('logs'))
    log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE, verbose_name=_('log file'))
    
    def __unicode__(self):
        return "%s" % self.name
    
    class Meta:
        verbose_name = _('logs clipboard')
        verbose_name_plural = _('logs clipboard')