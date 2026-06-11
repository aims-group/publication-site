FROM traefik:2.10

RUN apk add gettext

RUN mkdir -p /etc/traefik/ssl

# Prepare built-time variables for template
ARG host_name
ARG backend_prefix

ENV HOST_NAME=$host_name
ENV BACKEND_PREFIX=$backend_prefix

# Convert template to traefik.yml
COPY dynamic.tmpl /dynamic.tmpl
COPY traefik.tmpl /traefik.tmpl
COPY make_traefik.sh /make_traefik.sh
RUN chmod +x /make_traefik.sh
RUN ./make_traefik.sh
RUN rm traefik.tmpl
RUN rm make_traefik.sh