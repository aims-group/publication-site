FROM traefik:2.10

RUN apk add gettext
RUN mkdir -p /etc/traefik/acme
RUN touch /etc/traefik/acme/acme.json
RUN chmod 600 /etc/traefik/acme/acme.json

# Prepare built-time variables for template
ARG host_name
ARG backend_prefix
ARG ssl_cert_file
ARG ssl_cert_key

ENV HOST_NAME=$host_name
ENV BACKEND_PREFIX=$backend_prefix

# Copy SSL certificate and key to container
RUN mkdir -p /etc/traefik/ssl
COPY $ssl_cert_file /etc/traefik/ssl/cert.pem
COPY $ssl_cert_key /etc/traefik/ssl/key.pem

# Convert template to traefik.yml
COPY traefik.tmpl /traefik.tmpl
COPY make_traefik.sh /make_traefik.sh
RUN chmod +x /make_traefik.sh
RUN ./make_traefik.sh
RUN rm traefik.tmpl
RUN rm make_traefik.sh
