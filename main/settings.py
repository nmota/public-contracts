"""
This is the entry point settings of manage.py runserver and wsgi.py.
(I.e. we use it in production)

What this module does depends on (1) whether module `settings_local` exists
and (2) how the value of `settings_local.HOST_NAME` compares with
`socket.gethostname()`. Specifically, this module:

- tries to import `settings_local`. If it doesn't exist, uses DEBUG mode
(LIVE = False);

- if `settings_local` exists, checks if the machine name (`socket.gethostname(
)`) is equal to `settings_local.HOST_NAME`. If `settings_local.HOST_NAME` doesn't
exist or the names are different, uses DEBUG mode. Otherwise, LIVE = True;

- In DEBUG mode, it ignores `settings_local` and uses the settings defined
in this module;

- In LIVE mode, it tries to overwrite some settings in this module
with settings in `settings_local`.

Mandatory settings in `settings_local` for LIVE mode:
- `ALLOWED_HOSTS`
- `SECRET_KEY`

Optional settings in `settings_local` for LIVE or DEBUG:
- `CACHES`

Optional settings in `settings_local` for LIVE mode:
- `ADMINS`
- `EMAIL_HOST`
- `DATABASES`
- `STATIC_ROOT`
- `STATIC_URL`

"""
import socket
import os.path

# e.g. SITE_DOMAIN = 'www.example.com'
from .domain import SITE_DOMAIN

try:
    from . import settings_local
except ImportError:
    settings_local = object


if hasattr(settings_local, 'HOST_NAME') and \
        socket.gethostname() == settings_local.HOST_NAME:
    LIVE = True
    DEBUG = False
    TEMPLATE_DEBUG = False
else:
    LIVE = False
    DEBUG = True
    TEMPLATE_DEBUG = True

main_directory = os.path.abspath(os.path.dirname(__file__))
site_directory = os.path.abspath(os.path.dirname(main_directory))


############## Email and email receivers ##############
if LIVE and hasattr(settings_local, 'ADMINS'):
    ADMINS = settings_local.ADMINS
    MANAGERS = ADMINS

if LIVE and hasattr(settings_local, 'EMAIL_HOST'):
    EMAIL_HOST = settings_local.EMAIL_HOST
    EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
    SERVER_EMAIL = settings_local.SERVER_EMAIL
    EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_DOMAIN


############## Databases ##############
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'publics',
        'USER': 'publics_read_only',
        'PASSWORD': r'read-only',
        'HOST': '5.153.9.51',
        'PORT': '5432',
    },
    'old': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'contracts',
        'USER': 'public_contracts',
        'PASSWORD': 'read-only',
        'HOST': '5.153.9.51',
        'PORT': '3306',
    }
}

if LIVE and hasattr(settings_local, 'DATABASES'):
    DATABASES = settings_local.DATABASES


############## Security settings ##############

# We force `settings_local` to contain `ALLOWED_HOSTS` so we don't go live
# with all hosts allowed
ALLOWED_HOSTS = ['*']
if LIVE:
    ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS

# We force `settings_local` to contain a `SECRET_KEY` so we don't go live
# with a public key
SECRET_KEY = 'a_public_key'
if LIVE:
    SECRET_KEY = settings_local.SECRET_KEY

############## Time zones and internationalization ##############
TIME_ZONE = 'Europe/Lisbon'
LANGUAGE_CODE = 'pt'

LANGUAGES = (('en', 'English'),
             ('pt', 'Portuguese'))

USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (site_directory + '/locale',)

############## Location of the static files ##############
STATIC_ROOT = os.path.join(main_directory, 'static')
if LIVE and hasattr(settings_local, 'STATIC_ROOT'):
    STATIC_ROOT = settings_local.STATIC_ROOT

STATIC_URL = '/static/'
if LIVE:
    STATIC_URL = 'http://%s/static/' % SITE_DOMAIN


############## Django specifics ##############
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'main.urls'
WSGI_APPLICATION = 'main.apache.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.tz",
                               "django.core.context_processors.request",
                               "main.context_processors.site",)

INSTALLED_APPS = (
    'main',
    'contracts',
    'deputies',
    'law',
    'treebeard',  # for model in trees
    'sphinxql',   # for search
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES


############## Caches ##############
# We don't need to be LIVE to have caching.
if hasattr(settings_local, 'CACHES'):
    CACHES = settings_local.CACHES


############## Django-SphinxQL specifics ##############
INDEXES = {
    'path': os.path.join(site_directory, '_index'),
    'sphinx_path': site_directory,
    'index_params': {
        'charset_table':
        'U+00C0..U+00C3->U+00E0..U+00E3, U+00E0..U+00E3, '  # Á..Â -> á..â
        'U+00EA, U+00CA->U+00EA, '  #Ê -> ê
        'U+00E9, U+00C9->U+00E9, '  #É -> é
        'U+00ED, U+00CD->U+00ED, '  #Í -> í
        'U+00F2..U+00F5, U+00D2..U+00D5->U+00F2..U+00F5, '  #Ó -> ó
        'U+00FA, U+00DA->U+00FA, '  #Ú -> ú
        'U+00E7, U+00C7->U+00E7, '  #Ç -> ç
        '0..9, A..Z->a..z, _, a..z, '
        '/->/',
    },
}


############## Logging ##############
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        # If in debug, DEBUG to console
        'debug_console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # If no debug, INFO to console.
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # If no debug, errors to admins
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['debug_console', 'console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
