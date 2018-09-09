from gradestats.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'collected_static/')
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media/')
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'change_this_to_something_secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gradestats',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'postgres.service.consul',
        'PORT': '5432',
    }
}
