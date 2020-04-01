FROM python:3.7.4-alpine

RUN apk update && \
    apk add --no-cache --virtual build-deps python-dev postgresql-dev git python3-dev gcc musl-dev \
        jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev \
        tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev

RUN pip3 install --upgrade pip setuptools \
    && wget -qO- https://github.com/jwilder/dockerize/releases/download/v0.2.0/dockerize-linux-amd64-v0.2.0.tar.gz | tar -zxf - -C /usr/bin \
    && chown root:root /usr/bin/dockerize

WORKDIR /opt/

ARG ENVIRONMENT=dev

ENV ENVIRONMENT=${ENVIRONMENT}
ENV DJANGO_SETTINGS_MODULE=ro_help.settings.${ENVIRONMENT}

# Copy just the requirements for caching
COPY ./requirements* /opt/
RUN pip3 install -r requirements-${ENVIRONMENT}.txt

COPY ./docker/web/docker-entrypoint /
COPY ./ /opt/

WORKDIR /opt/ro_help/

RUN if [ "ENVIRONMENT" == "prod" ]; then ./manage.py collectstatic; fi

ENTRYPOINT ["/docker-entrypoint"]
EXPOSE 8000
