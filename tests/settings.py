"""Minimal Django settings for running the logtailer test suite standalone."""
import tempfile

SECRET_KEY = 'logtailer-test-suite-secret-key'

# Test log files are created with tempfile (see logtailer/tests/utils.py).
LOGTAILER_ALLOWED_ROOTS = [tempfile.gettempdir()]

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'logtailer',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_URL = 'static/'

USE_TZ = True

LANGUAGE_CODE = 'en-us'

# Mirror what modern host projects use; logtailer pins its own
# default_auto_field in apps.py, which must override this.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
