import os
import tempfile

from django.contrib.auth.models import User


def make_temp_log(content, suffix='.log'):
    """Create a temp file with the given content, return its path.

    Caller is responsible for removing it (use addCleanup).
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


def create_staff_user(username='staff', password='password'):
    return User.objects.create_user(
        username=username, password=password, is_staff=True)


def create_superuser(username='admin', password='password'):
    return User.objects.create_superuser(
        username=username, password=password, email='admin@example.com')
