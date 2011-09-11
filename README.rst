=================================
Django LogTailer
=================================

:Version: 0.1
:Source: http://github.com/fireantology/django-logtailer/
--


Allows the viewing of any log file entries in real time directly from the Django admin interface.
It allows you to filter on logs with regex and offer also a log clipboard for save desired log lines to the django db.
This is a first beta version, don't expect so much.

Demos
========
- Demo `Video`_

.. _`Video`: http://www.vimeo.com/28889452

Requirements
========

- Django 1.3
- A working cache backend (used for store file cursor position)

Installation
========

- Copy the logtailer folder in you project and add it to the INSTALLED_APPS
- Run manage.py syncdb for create the required tables                                                                                                                          
- Create a symbolic link named 'logtailer' in you media root folder pointing to the logtailer media folder, alternatively you can also copy the logtailer media folder in your media root