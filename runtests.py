#!/usr/bin/env python
"""Standalone test runner for django-logtailer.

Usage: python runtests.py [test labels...]
"""
import os
import sys

import django
from django.test.utils import get_runner
from django.conf import settings


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    django.setup()
    test_runner = get_runner(settings)(verbosity=2)
    labels = sys.argv[1:] or ['logtailer']
    failures = test_runner.run_tests(labels)
    sys.exit(bool(failures))


if __name__ == '__main__':
    main()
