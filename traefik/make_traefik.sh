if [[ $BACKEND_PREFIX ]];
then
BACKEND_RULE="Host(\`$HOST_NAME\`) && PathPrefix(\`/$BACKEND_PREFIX\`)"
else
BACKEND_RULE="Host(\`$HOST_NAME\`)"
fi

export HOST_NAME=$HOST_NAME \
    BACKEND_RULE=$BACKEND_RULE && envsubst < traefik.tmpl > /etc/traefik/traefik.yml
