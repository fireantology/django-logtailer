import os

from django.conf import settings


def get_allowed_roots():
    """Return the configured allowed root directories.

    ``LOGTAILER_ALLOWED_ROOTS`` is a mandatory list of directories: log
    files can only be read from inside those directories (symlinks and
    ``..`` components are resolved first). If the setting is missing or
    empty, access to every path is denied (secure by default).
    """
    return getattr(settings, 'LOGTAILER_ALLOWED_ROOTS', None) or []


def is_path_allowed(path):
    """Check whether ``path`` is inside one of the allowed root dirs.

    The path is fully resolved (``os.path.realpath``) before checking, so
    path traversal (``..``) and symlinks pointing outside an allowed root
    are rejected. See CWE-22.
    """
    real_path = os.path.realpath(path)
    for root in get_allowed_roots():
        real_root = os.path.realpath(str(root))
        try:
            if os.path.commonpath([real_path, real_root]) == real_root:
                return True
        except ValueError:
            # Different drives (Windows) or mixed abs/relative paths.
            continue
    return False
