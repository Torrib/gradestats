FROM python:3.8-alpine3.11

LABEL maintainer=dotkom@online.ntnu.no

ENV NAME=gradestats
ENV DIR=/srv/app

RUN apk add --update --no-cache \
    postgresql-dev \
    build-base \
    libressl-dev \
    musl-dev \
    libffi-dev

RUN mkdir -p $DIR
WORKDIR $DIR

# Install requirements
COPY ./requirements.txt $DIR/requirements.txt
RUN pip --no-cache-dir install --upgrade pip
RUN pip --no-cache-dir install --upgrade -r requirements.txt

RUN apk del --purge build-base

# Copy project files
COPY . $DIR

RUN mkdir -p static media
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.prod
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8080
EXPOSE 8081

CMD ["sh", "docker-entrypoint.sh"]
