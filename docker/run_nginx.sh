#!/bin/sh

# create config file from template
echo $IMAGE_TAG
if [ "$IMAGE_TAG" = "local" ]; then
   echo "Running locally - dev mode"
   envsubst '$$NGINX_HOSTS' < /etc/nginx/conf.d/web.dev.template > /etc/nginx/conf.d/default.conf
elif [ "$IMAGE_TAG" = "prod" ]; then
   echo "Running in prod"
   envsubst '$$NGINX_HOSTS $$NGINX_SSL_FOLDER $$METABASE_HOST $$METABASE_SSL_FOLDER' < /etc/nginx/conf.d/web.prod.template > /etc/nginx/conf.d/default.conf
else
   echo "Running in dev or staging"
   envsubst '$$NGINX_HOSTS $$NGINX_SSL_FOLDER $$METABASE_HOST $$METABASE_SSL_FOLDER' < /etc/nginx/conf.d/web.devstaging.template > /etc/nginx/conf.d/default.conf
fi


while :;
do sleep 6h & wait ${!}; nginx -s reload;
done & nginx -g "daemon off;"
