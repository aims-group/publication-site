FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1

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

RUN addgroup --system django \
    && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.prod.txt /requirements.txt
RUN pip3 install --no-cache-dir -r /requirements.txt \
    && rm /requirements.txt

COPY ./docker/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./docker/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start

RUN mkdir /var/log/django
RUN chown django /var/log/django

RUN mkdir /pubhub
RUN chown django /pubhub

COPY --chown=django:django ./config /pubhub/config
COPY --chown=django:django ./publisher /pubhub/publisher
COPY --chown=django:django ./scripts /pubhub/scripts
COPY --chown=django:django ./templates /pubhub/templates
COPY --chown=django:django ./pubhub-static /pubhub/pubhub-static
COPY --chown=django:django ./manage.py /pubhub/manage.py

USER django

WORKDIR /pubhub

ENTRYPOINT ["/entrypoint"]