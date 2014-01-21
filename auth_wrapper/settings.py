# Django settings for VideoSearch project.
# From NB: https://github.com/nbproject/nbproject/blob/master/apps/settings.py
from os.path import abspath, dirname, basename
import os
import logging

FN_CREDENTIALS = "settings_credentials.py"
def msg_credentials():
    msg = "*** Please edit the %s file with the required settings for authentication. ***" %(FN_CREDENTIALS, )
    stars = "*" * len(msg)
    return "\n\n%s\n%s\n%s\n\n" %(stars, msg, stars)

try:
    import settings_credentials
except ImportError:
    from os.path import dirname, abspath
    import shutil
    thisdir = dirname(abspath(__file__))
    shutil.copy2("%s/%s.skel" % (thisdir, FN_CREDENTIALS), "%s/%s" % (thisdir, FN_CREDENTIALS))
    print msg_credentials()
    exit(1)

DEBUG = settings_credentials.__dict__.get("DEBUG", False)
TEMPLATE_DEBUG = DEBUG
ADMINS = settings_credentials.__dict__.get("ADMINS", ())
MANAGERS = ADMINS
SERVERNAME = settings_credentials.__dict__.get("SERVERNAME", "localhost")
HTTP_PORT = settings_credentials.__dict__.get("HTTP_PORT", "80")
CRON_EMAIL = settings_credentials.__dict__.get("CRON_EMAIL", "no@one.com")
DATABASES = settings_credentials.DATABASES

# For Amazon S3
S3_ACCESS_KEY = settings_credentials.__dict__.get("S3_ACCESS_KEY")
S3_SECRET_KEY = settings_credentials.__dict__.get("S3_SECRET_KEY")
S3_BUCKET_NAME = settings_credentials.__dict__.get("S3_BUCKET_NAME")
OUTPUT_BUCKET = settings_credentials.__dict__.get("OUTPUT_BUCKET")
TRANSCODER_ENDPOINT = settings_credentials.__dict__.get("TRANSCODER_ENDPOINT")
CLOUDFRONT_SERVER = settings_credentials.__dict__.get("CLOUDFRONT_SERVER")

# For configuring the Amazon Transcoder:
PIPELINE_ID = settings_credentials.__dict__.get("PIPELINE_ID")
HLS_2M = settings_credentials.__dict__.get("HLS_2M")
HLS_1M = settings_credentials.__dict__.get("HLS_1M")
HLS_400K = settings_credentials.__dict__.get("HLS_400K")
MP4_1080P = settings_credentials.__dict__.get("MP4_1080P")
MP4_480P_43 = settings_credentials.__dict__.get("MP4_480P_43")
MP4_320X240 = settings_credentials.__dict__.get("MP4_320X240")

# For logging
LOGGING = settings_credentials.__dict__.get('LOGGING')

# For static and media files
MEDIA_ROOT = settings_credentials.__dict__.get('MEDIA_ROOT')
MEDIA_URL = settings_credentials.__dict__.get('MEDIA_URL')
STATIC_ROOT = settings_credentials.__dict__.get('STATIC_ROOT')
STATIC_URL = settings_credentials.__dict__.get('STATIC_URL')
CLICK_ROOT = settings_credentials.__dict__.get('CLICK_ROOT')

# For logging in
LOGIN_URL = settings_credentials.__dict__.get('LOGIN_URL')

# For MC3 Configuration
MC3_HOST = settings_credentials.__dict__.get('MC3_HOST')
MC3_SERVICES = settings_credentials.__dict__.get('MC3_SERVICES')

#For functional tests
SELENIUM_WEBDRIVER = settings_credentials.__dict__.get('SELENIUM_WEBDRIVER')

# For the learning manager
MANAGER_MODULE = settings_credentials.__dict__.get('MANAGER_MODULE')

# For allowed hosts (Django 1.5+, Debug = False)
ALLOWED_HOSTS = settings_credentials.__dict__.get('ALLOWED_HOSTS')

# For the secure Touchstone login
SECURE_PATH = settings_credentials.__dict__.get('SECURE_PATH')

if "default" not in DATABASES or "PASSWORD" not in DATABASES["default"] or DATABASES["default"]["PASSWORD"]=="":
    print msg_credentials()
    exit(1)

# PROJECT_PATH avoids using a hard-coded path that must be changed with every server deployment
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ABS_PATH_TO_FILES = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

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



# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2!_p3jw05qr&amp;!i*q-nrhjjkq0b4@*_oz4sn400*3$s+0r@n$m)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    #'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
)

#CACHE_MIDDLEWARE_ALIAS = settings_credentials.__dict__.get('CACHE_MIDDLEWARE_ALIAS')
#CACHE_MIDDLEWARE_SECONDS = settings_credentials.__dict__.get('CACHE_MIDDLEWARE_SECONDS')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

ROOT_URLCONF = 'video_search.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'video_search.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #'/usr/local/pythonenv/videos_vm/video_search/templates',
    ABS_PATH_TO_FILES+'/templates'
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.tz",
	"django.contrib.messages.context_processors.messages",
	"django.core.context_processors.request",
)


INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'vcb',
    'debug_toolbar',
    'functional_tests',
    'mc3_learning_adapter_py',
    'south',
)

#INTERNAL_IPS = ('127.0.0.1', '18.189.97.96')

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)


# For mc3-learning-adapter-py
##
# The url of the handcar service application. At some point this will 
# likely go away:
HANDCAR = 'http://' + MC3_HOST + '/handcar'

##
# Make up an authority to use for any implementation assembled Osid Ids
AUTHORITY = MC3_HOST

##
# The display text types for this instance of hc_learning:
LANGUAGE_TYPE_ID = '639-2%3AEnglish%40ISO'
SCRIPT_TYPE_ID = '15924%3ALatin%40ISO'
FORMAT_TYPE_ID = 'Text+Formats%3Aplain%40okapia.net'

##
# Dictionary of the default genusTypeIds for various objects, indexed by 
# Id namespace:
DEFAULT_GENUS_TYPES = {
    'learning.Objective': 'mc3-objective%3Amc3.learning.topic%40MIT-OEIT',
    'learning.Activity': 'mc3-activity%3Amc3.learning.activity.asset.based%40MIT-OEIT',
    'learning.ObjectiveBank': 'mc3-objectivebank%3Amc3.learning.objectivebank.sandbox%40MIT-OEIT'
}

##
# The following metadata elements will be used to validate forms prior to 
# being posted to handcar. This implementation can assert any metadata
# restrictions it wishes. Just make sure these fall within any parameters 
# required by handcar itself. For instance, strings maximum lengths should
# be less than or equal to the max lengths imposed by handcar.
METADATA = {
    'comment': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'osid.OsidForm',
            'identifier': 'comment'
            },
        'element_label': 'Comment',
        'instructions': 'Optional form submission comment, 255 character maximum',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'STRING',
        'array': False,
        'minimum_string_length': 0, 
        'maximum_string_length': 256, 
        'string_set': []
    },
    'display_name': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'osid.OsidObjectForm',
            'identifier': 'displayName'
            },
        'element_label': 'Display Name',
        'instructions': 'Optional (default value will be provided by system), 255 character maximum',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'STRING',
        'array': False,
        'minimum_string_length': 0, 
        'maximum_string_length': 256, 
        'string_set': []
    },
    'description': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'osid.OsidObjectForm',
            'identifier': 'description'
            },
        'element_label': 'Description',
        'instructions': 'Optional (default value will be provided by system), 255 character maximum',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'STRING',
        'array': False,
        'minimum_string_length': 0, 
        'maximum_string_length': 256, 
        'string_set': []
    },
    'genus_type': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'osid.OsidObjectForm',
            'identifier': 'genus_type'
            },
        'element_label': 'Genus Type',
        'instructions': 'Required genus Type of type osid.type.Type',
        'required': True,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'TYPE',
        'array': False,
        'type_set': []
    },
    'assessment_id': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'learning.ObjectiveForm',
            'identifier': 'assessment'
            },
        'element_label': 'Assessment',
        'instructions': 'Optional assessment Id of type osid.id.Id',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'ID',
        'array': False,
        'id_set': []
    },
    'knowledge_category_id': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'learning.ObjectiveForm',
            'identifier': 'knowledge_category'
            },
        'element_label': 'Knowledge Category',
        'instructions': 'Optional knowledge category Id of type osid.id.Id',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'ID',
        'array': False,
        'id_set': []
    },
    'cognitive_process_id': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'learning.ObjectiveForm',
            'identifier': 'cognitive_process'
            },
        'element_label': 'Cognitive Process',
        'instructions': 'Optional cognitive process Id of type osid.id.Id',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'ID',
        'array': False,
        'id_set': []
    },
    'asset_ids': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'learning.ActivityForm',
            'identifier': 'assets'
            },
        'element_label': 'Assets',
        'instructions': 'Optional Asset Id list of type osid.id.Id',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'ID',
        'array': True,
        'id_set': []
    },
    'course_ids': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'learning.ActivityForm',
            'identifier': 'courses'
            },
        'element_label': 'Courses',
        'instructions': 'Optional Course Id list of type osid.id.Id',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'ID',
        'array': True,
        'id_set': []
    },
    'assessment_ids': {
        'element_id': {
            'authority': AUTHORITY,
            'namespace': 'learning.ActivityForm',
            'identifier': 'assessments'
            },
        'element_label': 'Assessments',
        'instructions': 'Optional Assessment Id list of type osid.id.Id',
        'required': False,
        'value': False,
        'read_only': False,
        'linked': False,
        'syntax': 'ID',
        'array': True,
        'id_set': []
    },
}