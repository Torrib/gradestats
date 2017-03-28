from gradestats.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ['www.grades.no']

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'collected_static/')
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media/')
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'change_this_to_something_secret'