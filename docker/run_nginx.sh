#!/bin/sh

# create config file from template
if [ "$IMAGE_TAG" = "local" ]; then
   envsubst '$$NGINX_HOSTS' < /etc/nginx/conf.d/web.dev.template > /etc/nginx/conf.d/default.conf
else
   envsubst '$$NGINX_HOSTS $$NGINX_SSL_FOLDER' < /etc/nginx/conf.d/web.template > /etc/nginx/conf.d/default.conf
fi    

while :;
do sleep 6h & wait ${!}; nginx -s reload;
done & nginx -g "daemon off;"
