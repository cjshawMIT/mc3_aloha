# updated cshaw, July 10, 2013
# to fit local directory structure, for development

import os
import sys

sys.path.insert(0, '/var/www/vcb_dev/VideoSearch_master/video_search/')
sys.path.insert(1, '/var/www/vcb_dev/VideoSearch_master/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'video_search.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
