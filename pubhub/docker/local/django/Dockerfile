FROM python:3.9-slim-buster

#ENV DATABASE_URL postgres://postgres:postgres@postgres:5432/postgres
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential \
    # psycopg2 dependencies
    && apt-get install -y libpq-dev \
    # Translations dependencies
    && apt-get install -y gettext \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

COPY ./docker/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

RUN mkdir /pubhub

COPY ./config /pubhub/config
COPY ./publisher /pubhub/publisher
COPY ./scripts /pubhub/scripts
COPY ./templates /pubhub/templates
COPY ./pubhub-static /pubhub/pubhub-static
COPY ./manage.py /pubhub/manage.py

WORKDIR /pubhub

ENTRYPOINT ["/entrypoint"]