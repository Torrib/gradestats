#!/usr/bin/env sh
python3 manage.py migrate


echo Starting uwsgi.
exec uwsgi --chdir=/srv/app \
    --plugins=python3,http \
    --module=gradestats.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=gradestats.settings.prod \
    --master --pidfile=/tmp/gradestats.pid \
    --socket=0.0.0.0:8080 \
    --http=0.0.0.0:8081 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --offload-threads=4 \
    --static-map=/static=/srv/app/collected_static \
    --static-map=/media=/srv/app/media \
    --vacuum
