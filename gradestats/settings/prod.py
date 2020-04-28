from gradestats.settings.base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['*']

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'collected_static/')
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media/')
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('GRADESTATS_SECRET', 'change_this_to_something_secret')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('GRADESTATS_DB_NAME', 'gradestats'),
        'USER': os.environ.get('GRADESTATS_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('GRADESTATS_DB_PASSWORD', ''),
        'HOST': os.environ.get('GRADESTATS_DB_HOST', 'localhost'),
        'PORT': os.environ.get('GRADESTATS_DB_PORT', '5432')
    }
}
