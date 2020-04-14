=================================
Django LogTailer
=================================

:Version: 1.1
:Source: http://github.com/fireantology/django-logtailer/


Allows the viewing of any log file entries in real time directly from the Django admin interface.
It allows you to filter on logs with regex and offer also a log clipboard for save desired log lines to the django db.

Demos
========
- Demo `Video`_

.. _`Video`: http://www.vimeo.com/28891014

Requirements
=============

- Django > 1.8
- Python 3.x or 2.X
- Sessions enabled

Installation
============

- Install the package with pip install django-logtailer
- Add it to the INSTALLED_APPS in your SETTINGS
- add to urls.py: url(r'^logs/', include('logtailer.urls')),
- Run manage.py migrate for create the required tables
- Run manage.py collectstatic

SETTING OPTIONS AVAILABLE
==========================

 - LOGTAILER_HISTORY_LINES , Number of line to get back from the file on first read, default value is 0