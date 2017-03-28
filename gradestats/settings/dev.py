from gradestats.settings.base import *

DEBUG = True

ALLOWED_HOSTS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!lb^1kz*y+!7%p^x8@ow+cm+m+u%5r*ra^#ozmq%_9vde9cel7'

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static/')
STATIC_URL = '/static/'