FROM alpine:latest

MAINTAINER Håvard Lian

ENV NAME=gradestats

ENV DIR=/srv/app

RUN apk add --update --no-cache \
    uwsgi-python3 \
    uwsgi-http \
    uwsgi-corerouter

RUN mkdir -p $DIR
WORKDIR $DIR

# Install requirements
COPY ./requirements.txt $DIR/requirements.txt
RUN pip3 --no-cache-dir install --upgrade pip
RUN pip3 --no-cache-dir install --upgrade -r requirements.txt

# Copy project files
COPY . $DIR

RUN mkdir -p static media
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.prod
RUN python3 manage.py collectstatic --noinput --clear

EXPOSE 8080
EXPOSE 8081

CMD ["sh", "docker-entrypoint.sh"]
