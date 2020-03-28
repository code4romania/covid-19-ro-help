FROM python:3.7.4-alpine

RUN apk update && \
    apk add --no-cache --virtual build-deps python-dev postgresql-dev git python3-dev gcc musl-dev \
        jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev \
        tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev

RUN pip3 install --upgrade pip setuptools \
    && wget -qO- https://github.com/jwilder/dockerize/releases/download/v0.2.0/dockerize-linux-amd64-v0.2.0.tar.gz | tar -zxf - -C /usr/bin \
    && chown root:root /usr/bin/dockerize

WORKDIR /opt/ro_help

ARG ENVIRONMENT=dev
ENV DJANGO_SETTINGS_MODULE=ro_help.settings.${ENVIRONMENT}

# Copy just the requirements for caching
COPY ./requirements* /opt/ro_help/
RUN pip3 install -r requirements-${ENVIRONMENT}.txt

COPY ./ /opt/ro_help

WORKDIR /opt/ro_help/ro_help

ENTRYPOINT ["/opt/ro_help/docker/web/docker-entrypoint"]
EXPOSE 8000
