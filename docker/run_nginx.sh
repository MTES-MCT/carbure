#!/bin/sh

# create config file from template
echo $IMAGE_TAG
if [ "$IMAGE_TAG" = "local" ]; then
   echo "Running locally - dev mode"
   envsubst '$$NGINX_HOSTS' < /etc/nginx/conf.d/web.dev.template > /etc/nginx/conf.d/default.conf
else
   echo "Running in a server - $IMAGE_TAG"
   envsubst '$$NGINX_HOSTS $$NGINX_SSL_FOLDER $$METABASE_HOST $$METABASE_SSL_FOLDER' < /etc/nginx/conf.d/web.template > /etc/nginx/conf.d/default.conf
fi    

while :;
do sleep 6h & wait ${!}; nginx -s reload;
done & nginx -g "daemon off;"
