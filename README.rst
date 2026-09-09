=================================
Django LogTailer
=================================

:Version: 1.3
:Source: http://github.com/fireantology/django-logtailer/


Allows the viewing of any log file entries in real time directly from the Django admin interface.
It allows you to filter on logs with regex and offer also a log clipboard for save desired log lines to the django db.

Demos
========
- Demo `Video`_

.. _`Video`: http://www.vimeo.com/28891014

Requirements
=============

- Django >= 6.1.1
- Python >= 3.12
- Sessions enabled

Installation
============

- Install the package with pip install django-logtailer
- Add it to the INSTALLED_APPS in your SETTINGS
- add to urls.py: url(r'^logs/', include('logtailer.urls')),
- Run manage.py migrate for create the required tables
- Run manage.py collectstatic

Settings
========

``LOGTAILER_ALLOWED_ROOTS`` (optional, strongly recommended): list of
directories log files are allowed to live in. Paths are fully resolved
(symlinks and ``..`` included) before checking, preventing path traversal
(CWE-22). When the setting is not defined, any path readable by the Django
process is allowed (legacy behaviour)::

    LOGTAILER_ALLOWED_ROOTS = ['/var/log/myapp']

Running tests
=============

From the repository root::

    python runtests.py

The suite uses a minimal standalone settings module (``tests/settings.py``)
with an in-memory SQLite database, so no extra setup is needed.
