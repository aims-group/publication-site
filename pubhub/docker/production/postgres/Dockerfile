FROM postgres:12.6

COPY ./docker/production/postgres/maintenance /usr/local/bin/maintenance

COPY ./docker/local/postgres/init.sql /docker-entrypoint-initdb.d/init.sql

RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
