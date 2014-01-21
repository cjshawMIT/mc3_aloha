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

# For logging
LOGGING = settings_credentials.__dict__.get('LOGGING')

# For static and media files
MEDIA_ROOT = settings_credentials.__dict__.get('MEDIA_ROOT')
MEDIA_URL = settings_credentials.__dict__.get('MEDIA_URL')
STATIC_ROOT = settings_credentials.__dict__.get('STATIC_ROOT')
STATIC_URL = settings_credentials.__dict__.get('STATIC_URL')

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
SECRET_KEY = '2!_p3jw05qr&amp;!i*q-nrhjjop0b7@*_oz4sn400*3$s+0r@n$m)'

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
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    #'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
)


ROOT_URLCONF = 'auth_wrapper.urls'

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
    'aloha',
    'functional_tests',
    'south',
)