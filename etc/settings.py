# Django settings for comms project.

import os
from .paths import PROJECT_NAME, TOP_DIR, BASE_APP_DIR, DATA_DIR
from django.conf import global_settings as gs

# This needs raised later ;)
CAMPAIGN_BLOCK_SIZE = 5  # 100

#
# Get server name
#

import socket
SERVER_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(SERVER_NAME)

#
# Base
#

DEBUG = TEMPLATE_DEBUG = True

ADMINS = (
    #('Trevor Joynson', 'trevorj@localhostsolutions.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, '%s.db' % PROJECT_NAME),
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
#MEDIA_ROOT = ''
MEDIA_ROOT = '%s/public/media/' % TOP_DIR

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
#MEDIA_URL = ''
MEDIA_URL = '/media/'

# Not useed anymore?
#ADMIN_MEDIA_PREFIX = '/static/admin/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
#STATIC_ROOT = ''
STATIC_ROOT = '%s/public/static2/' % TOP_DIR

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_APP_DIR, 'static'),
    #os.path.join(BASE_APP_DIR, 'public', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'jay(szyb48v&2b42x8re672-+v*-+#fjg#@h-xcb27f7)e_u)m'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = gs.MIDDLEWARE_CLASSES + (
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = '%s.urls' % PROJECT_NAME

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '%s.wsgi.application' % PROJECT_NAME

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_APP_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(name)s.%(module)s@%(funcName)s:%(lineno)d %(message)s',
            #'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            #'class': 'ConsoleHandler.ConsoleHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.db': {
            'level': 'INFO',
            'propagate': True,
        },
        #'django.request': {
        #    'handlers': ['mail_admins'],
        #    'level': 'ERROR',
        #    'propagate': True,
        #},
    }
}

""" Leftover stuff migrated """

#
# Project Apps
#
PROJECT_APPS = (
    #'base',
    #'health',
    #'campaign',
    #'api',
    #'emails',
    #'sms',
    'comms.campaign',
    'comms.emails',
    'comms.api',
    'comms.sms',
)
INSTALLED_APPS += PROJECT_APPS

#
# MongoDB (MongoEngine)
#

#MONGODB_DATABASES = {
#    'default': {'name': PROJECT_NAME}
#}

#import mongoengine
#mongoengine.connect(PROJECT_NAME)

##DJANGO_MONGOENGINE_OVERRIDE_ADMIN = True

## DB Router
##DATABASE_ROUTERS = ['solarsan.routers.MongoDBRouter', ]

## Auth
#AUTHENTICATION_BACKENDS = (
#    'mongoengine.django.auth.MongoEngineBackend',
#) + gs.AUTHENTICATION_BACKENDS

## Session Engine
#SESSION_ENGINE = 'mongoengine.django.sessions'

#
# Sessions
#

SESSION_COOKIE_NAME = PROJECT_NAME + '_sess'

#
# Misc crap for eays uncommenting
#

INSTALLED_APPS += (
    ## Third party libs
    #'south',
    #'djsupervisor',

    ##'sentry',
    ##'raven.contrib.django',
    #'breadcrumbs',
    #'jsonify',

    ##'tastypie',
    ##'tastypie_mongoengine',
    ##'backbone_tastypie',
)

#
# Celery
#
INSTALLED_APPS += ("djcelery", )
import djcelery
djcelery.setup_loader()

#
# South
#
INSTALLED_APPS += ("south", )

#
# Debug Toolbar
#
INSTALLED_APPS += (
    'debug_toolbar',
    #'debug_toolbar_mongo',
    #'debug_toolbar_autoreload',
)

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',          # Enable django-debug-toolbar
) + gs.MIDDLEWARE_CLASSES

DEBUG_TOOLBAR_PANELS = (
    # default panels
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    # 3rd
    #'debug_toolbar_mongo.panel.MongoDebugPanel',
    #'debug_toolbar_autoreload.AutoreloadPanel',
)

TEMPLATE_CONTEXT_PROCESSORS = gs.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.csrf',
    'django.core.context_processors.request',
)


def custom_show_toolbar(request):
    return True  # HACK
    try:
        if request.is_ajax():
            return False
        #if DEBUG: return True              # Show if DEBUG; default == DEBUG and if source ip in INTERNAL_IPS
        return request.user.is_superuser    # Show if logged in as a superuser
    except:
        return False

#DEBUG_TOOLBAR_MONGO_STACKTRACES = False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
    'HIDE_DJANGO_SQL': False,
    #'TAG': 'div',
    'ENABLE_STACKTRACES': True,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

INTERNAL_IPS = ['127.0.0.1']

#
# django-nose
#
#INSTALLED_APPS += ('django_nose', )
#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

#
# django-firstclass
#
#INSTALLED_APPS += ('firstclass', )
#EMAIL_BACKEND = 'firstclass.backends.ProxyBackend'

#
# django-newsletter
#
#INSTALLED_APPS += ('newsletter', )

#
# django-rest-framework
#
INSTALLED_APPS += ('rest_framework',
                   'rest_framework.authtoken')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        #'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.JSONPRenderer',
        'rest_framework.renderers.YAMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.XMLRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ),
    #'DEFAULT_PARSER_CLASSES': (
    #    'rest_framework.parsers.JSONParser',
    #    'rest_framework.parsers.FormParser'
    #),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        #'rest_framework.authentication.UserBasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'PAGINATE_BY': 10,
}

#
# django-extensions
#
INSTALLED_APPS += ('django_extensions', )

#
# django-devserver
#
#INSTALLED_APPS += ('devserver', )

#
# django-twilio
#
INSTALLED_APPS += ('django_twilio', )
TWILIO_ACCOUNT_SID = 'ACa7c819dd50324bbe628797e4012d36d8'
TWILIO_AUTH_TOKEN = '77355d83cf092fe32c951827d0214da4'
#TWILIO_DEFAULT_CALLERID = 'NNNNNNNNNN'

##
## mailchimp
##
#INSTALLED_APPS += ('mailchimp', )
#MAILCHIMP_API_KEY = '94f585822250e021af9cd84605177da0-us6'
#MAILCHIMP_WEBHOOK_KEY = 'demodemodemo'

##
## ActiveCampaign
##
#ACTIVECAMPAIGN_URL = 'https://trevorj.api-us1.com'
#ACTIVECAMPAIGN_API_KEY = '45e8225da1d10674f292f260a8717deff3585619ced9ba47f277816a02d40a821e2daa51'

## StreamSend
##Login ID: revyGrXZXsnF
##Key: WFnNE0U8e0t26k81

##
## iContact
##
#ICONTACT_APP_NAME = 'comms'
#ICONTACT_USER_NAME = 'icontact@skywww.net'
#ICONTACT_API_KEY = 'oppc6n3DSEUp4voxxNH2KBH72aEptEZt'
#ICONTACT_API_PASS = 'u39GC4wTqEs6navVvcJTe2e7zG9dUZ'

#
# something
#

#
# Celery (async tasks)
#

# When debugging,
if DEBUG:
    # Send events, started events, task sent events
    CELERY_SEND_EVENTS = True
    CELERY_SEND_TASK_SENT_EVENT = True
    CELERY_TRACK_STARTED = True

# Extra task modules (def=INSTALLED_APPS.tasks)
CELERY_IMPORTS = (
    # Enable HTTP dispatch task (http://celery.github.com/celery/userguide/remote-tasks.html)
    'celery.task.http',
)

CELERY_ROUTES = {
    'comms.campaign.tasks.queue': {'queue': 'campaigns'},
    'comms.campaign.tasks.send_email': {'queue': 'emails'},
    'comms.campaign.tasks.send_sms': {'queue': 'emails'},
}

#CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
#CELERY_ANNOTATIONS = {"*": {"rate_limit": "10/s"}}

CELERY_RESULT_BACKEND = "amqp"
CELERY_TASK_RESULT_EXPIRES = 3600

#
# django-celery-email
#
INSTALLED_APPS += ('djcelery_email', )
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

CELERY_EMAIL_TASK_CONFIG = {
    #'name': 'djcelery_email_send',
    #'ignore_result': True,
    #'queue': 'email',
    'rate_limit': '50/m',
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
